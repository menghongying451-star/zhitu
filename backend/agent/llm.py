"""
大模型调用封装（OpenAI 兼容协议）。

通义千问(DashScope)、DeepSeek、硅基流动(SiliconFlow)、Ollama、vLLM 等都兼容该协议，
换模型只需改 .env，不用改代码。
"""
import json
import logging
import re
from typing import Iterator, List, Optional

from . import conf

logger = logging.getLogger(__name__)

_THINK_RE = re.compile(r"<think>.*?</think>", re.S)


class LLMError(RuntimeError):
    pass


def strip_think(text: str) -> str:
    """去掉推理模型输出的 <think>...</think> 段。"""
    return _THINK_RE.sub("", text or "").strip()


def parse_json(text: str) -> dict:
    """尽量从模型输出中解析出一个 JSON 对象。"""
    text = strip_think(text)
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # 兜底：截取第一个 { 到最后一个 }
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            data = json.loads(text[start:end + 1])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    raise LLMError(f"模型输出不是合法 JSON: {text[:200]}")


class LLMClient:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = conf.llm_api_key()
            if not api_key:
                raise LLMError("未配置 AGENT_LLM_API_KEY，请在 .env 中填写大模型 API Key")
            from openai import OpenAI

            self._client = OpenAI(
                api_key=api_key,
                base_url=conf.llm_base_url(),
                timeout=conf.llm_timeout(),
                max_retries=2,
            )
        return self._client

    # ---- 基础调用 -------------------------------------------------------
    def chat(self, messages: List[dict], model: Optional[str] = None,
             temperature: float = 0.3, json_mode: bool = False) -> str:
        kwargs = dict(model=model or conf.llm_model(), messages=messages, temperature=temperature)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = self.client.chat.completions.create(**kwargs)
        except Exception as e:  # 部分模型不支持 response_format，降级重试一次
            if json_mode:
                logger.warning("json_mode 调用失败，降级为普通调用: %s", e)
                kwargs.pop("response_format", None)
                resp = self.client.chat.completions.create(**kwargs)
            else:
                raise LLMError(str(e)) from e
        return strip_think(resp.choices[0].message.content or "")

    def stream(self, messages: List[dict], model: Optional[str] = None,
               temperature: float = 0.5) -> Iterator[str]:
        try:
            resp = self.client.chat.completions.create(
                model=model or conf.llm_model(), messages=messages,
                temperature=temperature, stream=True,
            )
        except Exception as e:
            raise LLMError(str(e)) from e
        in_think = False
        for chunk in resp:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if not delta:
                continue
            # 过滤流式输出里的 <think> 段
            if "<think>" in delta:
                in_think = True
                delta = delta.split("<think>", 1)[0]
            if in_think:
                if "</think>" in delta:
                    in_think = False
                    delta = delta.split("</think>", 1)[1]
                else:
                    continue
            if delta:
                yield delta

    # ---- 结构化输出 -----------------------------------------------------
    def chat_json(self, system: str, user: str, model: Optional[str] = None) -> dict:
        messages = [
            {"role": "system", "content": system + "\n\n只输出一个 JSON 对象，不要输出任何其他文字。"},
            {"role": "user", "content": user},
        ]
        text = self.chat(messages, model=model or conf.llm_fast_model(), temperature=0.1, json_mode=True)
        try:
            return parse_json(text)
        except LLMError:
            # 再给一次机会
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": "上面的输出不是合法 JSON，请只输出 JSON 对象。"})
            text = self.chat(messages, model=model or conf.llm_fast_model(), temperature=0, json_mode=True)
            return parse_json(text)


_llm: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm


def set_llm(client) -> None:
    """测试时注入假的 LLM。"""
    global _llm
    _llm = client
