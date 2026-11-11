"""对话落库与读取（memory.py 管 2 小时内的上下文，这里管长期记录）。"""
import logging

from .models import ChatConversation, ChatMessage

logger = logging.getLogger(__name__)

TITLE_LEN = 40


def record_turn(agent: str, user, conversation_id: str, inputs: dict,
                user_text: str, answer: str, actions: list) -> None:
    """记录一轮对话。失败只记日志，绝不影响聊天本身。"""
    try:
        conv, created = ChatConversation.objects.get_or_create(
            id=conversation_id,
            defaults={"user": user, "agent": agent, "inputs": inputs or {},
                      "title": (user_text or "新对话").strip().replace("\n", " ")[:TITLE_LEN]},
        )
        if conv.user_id != user.pk:  # 会话 ID 不属于当前用户，不写
            return
        ChatMessage.objects.bulk_create([
            ChatMessage(conversation=conv, role="user", content=user_text),
            ChatMessage(conversation=conv, role="assistant", content=answer, actions=actions or []),
        ])
        if not created:
            conv.save(update_fields=["updated_at"])
    except Exception as e:  # noqa: BLE001
        logger.warning("对话记录写入失败: %s", e)


def restore_history(agent: str, user, conversation_id: str, limit: int = 40) -> list:
    """缓存过期后，从数据库恢复最近的对话，让学生在历史记录里能接着聊。"""
    try:
        conv = ChatConversation.objects.filter(id=conversation_id, user=user, agent=agent).first()
        if not conv:
            return []
        msgs = list(conv.messages.order_by("-id")[:limit])[::-1]
        return [{"role": m.role, "content": m.content} for m in msgs]
    except Exception as e:  # noqa: BLE001
        logger.warning("对话记录读取失败: %s", e)
        return []
