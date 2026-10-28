"""
智能体 HTTP 接口

GET  /api/v1/agent/<name>/          智能体信息（开场白、推荐问题、是否支持上传）
POST /api/v1/agent/<name>/chat/     对话（默认 SSE 流式；加 ?stream=0 返回普通 JSON，方便 Postman 调试）

POST 参数（JSON 或 multipart/form-data）：
    query            用户输入
    conversation_id  会话 ID，首轮不传，由后端生成并在 meta 事件里返回
    inputs           JSON 对象，如 {"pid": 12, "tone": "严谨"}
    file             （multipart）上传文件

SSE 事件（每行 `data: {...}`）：
    {"type": "meta", "conversation_id": "..."}
    {"type": "delta", "text": "..."}
    {"type": "action", "name": "requirement_published", "data": {...}}
    {"type": "error", "message": "..."}
    {"type": "done"}
"""
import json
import logging

from asgiref.sync import sync_to_async
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.handlers.asgi import ASGIRequest
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import conf, memory
from .base import ChatContext
from .documents import DocumentError
from .llm import LLMError
from .registry import AGENTS, get_agent

logger = logging.getLogger(__name__)


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def _as_async(gen):
    """ASGI（daphne/uvicorn）下必须给异步迭代器，否则 Django 会把整段响应缓冲完才发送。"""
    sentinel = object()
    step = sync_to_async(lambda: next(gen, sentinel), thread_sensitive=True)
    while True:
        item = await step()
        if item is sentinel:
            break
        yield item


class AgentListView(APIView):
    def get(self, request):
        return Response([a.meta() for a in AGENTS.values()])


class AgentMetaView(APIView):
    def get(self, request, name):
        agent = get_agent(name)
        if not agent:
            return Response({"detail": "智能体不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(agent.meta())


class AgentChatView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, name):
        agent = get_agent(name)
        if not agent:
            return Response({"detail": "智能体不存在"}, status=status.HTTP_404_NOT_FOUND)
        denied = agent.check_permission(request.user)
        if denied:
            return Response({"detail": denied}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        query = (data.get("query") or "").strip()[:4000]
        conversation_id = (data.get("conversation_id") or "").strip() or memory.new_conversation_id()
        inputs = data.get("inputs") or {}
        if isinstance(inputs, str):
            try:
                inputs = json.loads(inputs)
            except ValueError:
                inputs = {}
        if not isinstance(inputs, dict):
            inputs = {}

        upload = request.FILES.get("file")
        if upload is not None:
            if not agent.allow_file:
                return Response({"detail": "该智能体不支持上传文件"}, status=status.HTTP_400_BAD_REQUEST)
            if upload.size > conf.MAX_UPLOAD_BYTES:
                return Response({"detail": "文件过大，请上传 15MB 以内的文件"}, status=status.HTTP_400_BAD_REQUEST)
            # 流式响应期间原始上传文件可能已被关闭，先读进内存
            upload = SimpleUploadedFile(upload.name, upload.read(), content_type=upload.content_type)
        if not query and upload is None:
            return Response({"detail": "请输入内容"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        state = memory.load(agent.name, user.pk, conversation_id)
        ctx = ChatContext(user=user, query=query, inputs=inputs, state=state,
                          conversation_id=conversation_id, file=upload)
        events = self._run(agent, ctx)

        if request.query_params.get("stream") in ("0", "false"):
            answer, actions = [], []
            for ev in events:
                if ev["type"] == "delta":
                    answer.append(ev["text"])
                elif ev["type"] in ("action", "error"):
                    actions.append(ev)
            return Response({"conversation_id": conversation_id, "answer": "".join(answer), "events": actions})

        body = (_sse(e) for e in events)
        if isinstance(getattr(request, "_request", request), ASGIRequest):
            body = _as_async(body)
        resp = StreamingHttpResponse(body, content_type="text/event-stream; charset=utf-8")
        resp["Cache-Control"] = "no-cache"
        resp["X-Accel-Buffering"] = "no"  # 关闭 Nginx 缓冲，保证逐字输出
        return resp

    @staticmethod
    def _run(agent, ctx: ChatContext):
        yield {"type": "meta", "conversation_id": ctx.conversation_id, "agent": agent.name}
        answer = []
        try:
            for ev in agent.run(ctx):
                if ev.get("type") == "delta":
                    answer.append(ev["text"])
                yield ev
        except DocumentError as e:
            msg = str(e)
            answer.append(msg)
            yield {"type": "delta", "text": msg}
        except LLMError as e:
            logger.error("[agent:%s] LLM 调用失败: %s", agent.name, e)
            msg = "抱歉，智能体暂时无法响应（大模型服务异常），请稍后再试。"
            answer.append(msg)
            yield {"type": "error", "message": msg}
        except Exception as e:  # noqa: BLE001
            logger.exception("[agent:%s] 运行出错: %s", agent.name, e)
            msg = "抱歉，处理过程中出现了问题，请稍后重试。"
            answer.append(msg)
            yield {"type": "error", "message": msg}
        finally:
            user_text = ctx.query or (f"[上传文件] {ctx.file.name}" if ctx.file else "")
            ctx.history.append({"role": "user", "content": user_text})
            ctx.history.append({"role": "assistant", "content": "".join(answer)[:4000]})
            memory.save(agent.name, ctx.user.pk, ctx.conversation_id, ctx.state)
        yield {"type": "done"}
