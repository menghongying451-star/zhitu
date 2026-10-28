"""
智能体基类。

每个智能体实现 run(ctx)，以生成器的方式产出事件（dict），由 views 转成 SSE 推给前端：
    {"type": "delta",  "text": "..."}     逐字输出的文本
    {"type": "action", "name": "...", "data": {...}}   需要前端配合的动作（如需求发布成功）
"""
from dataclasses import dataclass, field
from typing import Iterator, List, Optional

from . import conf
from .llm import get_llm


@dataclass
class ChatContext:
    user: object
    query: str
    inputs: dict
    state: dict
    conversation_id: str
    file: Optional[object] = None  # Django UploadedFile

    @property
    def vars(self) -> dict:
        return self.state.setdefault("vars", {})

    @property
    def history(self) -> List[dict]:
        return self.state.setdefault("history", [])

    @property
    def tone(self) -> str:
        return (self.inputs.get("tone") or self.vars.get("tone") or "").strip()


def tone_instruction(tone: str) -> str:
    """
    原 Dify 用一个「角色生成器」LLM 节点把用户给的风格词翻译成角色设定，
    这里直接写进 system prompt，少一次模型调用。
    """
    tone = (tone or "").strip()[:30] or "严谨"
    return (
        f"# 角色设定\n回答风格：{tone}。请把「{tone}」体现在语气和情绪倾向上"
        "（例如严谨=理性、干脆、有条理；活泼=亲切、轻松），但不要改变事实内容。"
    )


QA_RULES = """# 回答规范
1. 只依据 <context> 中的信息作答，不引入外部信息；严禁编造人名、项目名称、联系方式、数字和链接。
2. 先在 <context> 中找答案：找到就据实回答；找不到就明确说明“现有资料中没有提到”，再给出下一步建议，不得编造。
3. 不要提到 <context>、“上下文”标签等字样，用“相关资料”“项目信息”代替。
4. 全程使用中文，允许少量英文术语。
5. 如果用户表达焦虑（如“烦/焦虑/慌/救命”），先安抚一句再回答。
6. 可以基于资料做适度推断，但要说明是推断。
7. 用户的个人简介可有可无：有就结合它回答，没有也不要索要。
8. 格式：条理清晰，多步建议分条列出，适度使用 Markdown。"""


class BaseAgent:
    name = ""
    title = ""
    opening = ""
    suggestions: List[str] = []
    # 是否允许上传文件
    allow_file = False
    file_hint = ""

    @property
    def llm(self):
        return get_llm()

    def meta(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "opening": self.opening,
            "suggestions": self.suggestions,
            "allow_file": self.allow_file,
            "file_hint": self.file_hint,
            "accept": ",".join(sorted(conf.ALLOWED_DOC_EXT)),
        }

    def check_permission(self, user) -> Optional[str]:
        """返回错误信息表示无权使用。"""
        return None

    def run(self, ctx: ChatContext) -> Iterator[dict]:
        raise NotImplementedError

    # ---- 工具方法 ------------------------------------------------------
    @staticmethod
    def say(text: str) -> dict:
        return {"type": "delta", "text": text}

    def stream_answer(self, system: str, ctx: ChatContext, user_content: Optional[str] = None,
                      with_history: bool = True) -> Iterator[dict]:
        """流式调用大模型，逐段产出 delta 事件。"""
        messages = [{"role": "system", "content": system}]
        if with_history:
            messages += ctx.history[-conf.HISTORY_WINDOW:]
        messages.append({"role": "user", "content": user_content if user_content is not None else ctx.query})
        for piece in self.llm.stream(messages):
            yield self.say(piece)
