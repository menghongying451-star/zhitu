"""
会话记忆：替代 Dify 的 conversation variables。

存在 Django cache（项目已配置 Redis），按「智能体 + 用户 + 会话ID」隔离，
默认 2 小时过期。
"""
import uuid
from typing import Optional

from django.core.cache import cache

from . import conf


def _key(agent: str, user_id, conversation_id: str) -> str:
    return f"agent:conv:{agent}:{user_id}:{conversation_id}"


def new_conversation_id() -> str:
    return uuid.uuid4().hex


def load(agent: str, user_id, conversation_id: Optional[str]) -> dict:
    if conversation_id:
        state = cache.get(_key(agent, user_id, conversation_id))
        if state is not None:
            return state
    return {"history": [], "vars": {}}


def save(agent: str, user_id, conversation_id: str, state: dict) -> None:
    # 只保留最近 40 条历史，防止无限增长
    state["history"] = state.get("history", [])[-40:]
    cache.set(_key(agent, user_id, conversation_id), state, timeout=conf.session_ttl())


def clear(agent: str, user_id, conversation_id: str) -> None:
    cache.delete(_key(agent, user_id, conversation_id))
