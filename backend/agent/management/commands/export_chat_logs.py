"""
导出智能体对话记录，供期末用户测试做统计。

    python manage.py export_chat_logs                     # 导出到 chat_logs.csv
    python manage.py export_chat_logs -o test.csv --since 2026-12-21 --agent zhitu

每行一条消息：会话、用户、智能体、轮次、角色、内容、本轮收藏/发布等动作。
"""
import csv
import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from agent.models import ChatMessage


class Command(BaseCommand):
    help = "导出智能体对话记录为 CSV（Excel 可直接打开）"

    def add_arguments(self, parser):
        parser.add_argument("-o", "--output", default="chat_logs.csv")
        parser.add_argument("--since", help="只导出该日期之后的对话，如 2026-12-21")
        parser.add_argument("--agent", help="只导出某个智能体：zhitu / wenshi / tianbao")

    def handle(self, *args, **opts):
        qs = ChatMessage.objects.select_related("conversation__user").order_by("conversation_id", "id")
        if opts["since"]:
            since = timezone.make_aware(datetime.strptime(opts["since"], "%Y-%m-%d"))
            qs = qs.filter(conversation__created_at__gte=since)
        if opts["agent"]:
            qs = qs.filter(conversation__agent=opts["agent"])

        n, turns = 0, {}
        # utf-8-sig：Excel 双击打开不乱码
        with open(opts["output"], "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["会话ID", "用户名", "智能体", "轮次", "角色", "时间", "内容", "动作"])
            for m in qs:
                c = m.conversation
                if m.role == "user":
                    turns[c.id] = turns.get(c.id, 0) + 1
                w.writerow([c.id, c.user.username, c.agent, turns.get(c.id, 0), m.role,
                            timezone.localtime(m.created_at).strftime("%Y-%m-%d %H:%M"),
                            m.content, json.dumps(m.actions, ensure_ascii=False) if m.actions else ""])
                n += 1
        self.stdout.write(self.style.SUCCESS(f"已导出 {n} 条消息、{len(turns)} 个会话 → {opts['output']}"))
