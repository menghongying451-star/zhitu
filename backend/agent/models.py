"""
对话记录：把智能体的每一轮对话存进数据库。

- 学生端「历史对话」页面读这里；
- 期末用户测试时，用 `python manage.py export_chat_logs` 导出成 CSV 做统计
  （对话轮数、推荐/收藏了哪些机会）。
"""
from django.conf import settings
from django.db import models


class ChatConversation(models.Model):
    id = models.CharField("会话 ID", max_length=64, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="agent_conversations", verbose_name="用户")
    agent = models.CharField("智能体", max_length=32, db_index=True)
    title = models.CharField("标题", max_length=120, blank=True)
    inputs = models.JSONField("入参", default=dict, blank=True)
    created_at = models.DateTimeField("开始时间", auto_now_add=True)
    updated_at = models.DateTimeField("最后对话时间", auto_now=True)

    class Meta:
        verbose_name = "智能体会话"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user", "-updated_at"])]

    def __str__(self):
        return f"{self.agent} · {self.title or self.id}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "用户"), ("assistant", "智能体")]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE,
                                     related_name="messages", verbose_name="会话")
    role = models.CharField("角色", max_length=16, choices=ROLE_CHOICES)
    content = models.TextField("内容", blank=True)
    # 本轮触发的动作，如 [{"name": "requirement_favorited", "data": {"requirement_id": 3}}]
    actions = models.JSONField("动作", default=list, blank=True)
    created_at = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        verbose_name = "智能体消息"
        verbose_name_plural = verbose_name
        ordering = ["id"]
