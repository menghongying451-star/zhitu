"""
导入知途的种子机会数据。

    python manage.py seed_opportunities          # 导入 / 更新
    python manage.py seed_opportunities --reset  # 先删除之前导入的，再重新导入

数据来源（两个文件都会读）：
  agent/fixtures/opportunities.json       已整理好的公开机会（竞赛等）
  agent/fixtures/opportunities_extra.csv  自己补充的机会（实验室招人、实习等），可用 Excel 编辑
      列：标题,简介,详细要求,截止日期,人数,提供的支持,来源链接,领域,岗位
      截止日期写 YYYY-MM-DD，不确定就留空；领域/岗位填标签名称，多个用「、」分隔
      （标签名称见 tag_1 / tag_2 表，例如 软件和信息技术服务、互联网-人工智能-大模型算法）

所有机会挂在一个「知途运营团队」组织下，状态为进行中（学生可见）。
需要先执行 python manage.py loaddata tags。
"""
import csv
import datetime
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_PATH = os.path.join(HERE, "fixtures", "opportunities.json")
CSV_PATH = os.path.join(HERE, "fixtures", "opportunities_extra.csv")
ORG_NAME = "知途运营团队（整理自公开信息）"
OPS_USERNAME = "zhitu_ops"


def _split(v):
    return [x.strip() for x in (v or "").replace("，", "、").replace(",", "、").split("、") if x.strip()]


def _date(v):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return datetime.date.fromisoformat(v)
    except ValueError:
        raise CommandError(f"截止日期格式应为 YYYY-MM-DD：{v}")


class Command(BaseCommand):
    help = "导入知途种子机会数据"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="先删除之前导入的机会")

    def handle(self, *args, **opts):
        from organization.models import Organization
        from project.models import Requirement
        from user.models import OrganizationUser, Tag1, Tag2, User

        if not Tag1.objects.exists() or not Tag2.objects.exists():
            raise CommandError("标签表为空，请先执行：python manage.py loaddata tags")

        items = self._load()
        t1 = {t.value.strip(): t.id for t in Tag1.objects.all()}
        t2 = {t.post.strip(): t.id for t in Tag2.objects.all()}

        with transaction.atomic():
            org = Organization.objects.filter(name=ORG_NAME).first()
            if org is None:
                # bulk_create 跳过 Organization.save() 里面向真实入驻组织的认证校验
                Organization.objects.bulk_create([Organization(
                    name=ORG_NAME, organization_type="other", other_type="association",
                    industry_or_discipline="教育", scale="small",
                    business_scope="整理校园公开实践机会（竞赛、项目、实习等）",
                )])
                org = Organization.objects.get(name=ORG_NAME)
            user, created = User.objects.get_or_create(
                username=OPS_USERNAME, defaults={"email": "ops@zhitu.local"})
            if created:
                user.set_unusable_password()
                user.save()
            ops, _ = OrganizationUser.objects.get_or_create(user=user, defaults={"organization": org})

            if opts["reset"]:
                old = Requirement.objects.filter(organization=org)
                n = old.count()
                old.delete()
                self.stdout.write(f"已删除之前导入的机会 {n} 条")

            made = updated = 0
            for it in items:
                missing = [x for x in it["tag1"] if x not in t1] + [x for x in it["tag2"] if x not in t2]
                if missing:
                    self.stdout.write(self.style.WARNING(f"「{it['title']}」有找不到的标签，已跳过这些标签：{missing}"))
                desc = it["description"]
                if it.get("sources"):
                    desc += "\n\n信息来源：" + "；".join(it["sources"])
                fields = dict(
                    brief=it["brief"][:255], description=desc, status="in_progress",
                    publish_people=ops, finish_time=_date(it.get("finish_time")),
                    people_count=it.get("people_count"), support_provided=it.get("support_provided"),
                )
                req, is_new = Requirement.objects.update_or_create(
                    organization=org, title=it["title"][:255], defaults=fields)
                req.tag1.set([t1[x] for x in it["tag1"] if x in t1])
                req.tag2.set([t2[x] for x in it["tag2"] if x in t2])
                made += is_new
                updated += not is_new
        self.stdout.write(self.style.SUCCESS(f"完成：新增 {made} 条，更新 {updated} 条，共 {len(items)} 条机会"))

    def _load(self):
        with open(JSON_PATH, encoding="utf-8") as f:
            items = json.load(f)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    if not (row.get("标题") or "").strip():
                        continue
                    items.append({
                        "title": row["标题"].strip(), "brief": (row.get("简介") or "").strip(),
                        "description": (row.get("详细要求") or "").strip() or (row.get("简介") or "").strip(),
                        "finish_time": row.get("截止日期"), "people_count": (row.get("人数") or "").strip() or None,
                        "support_provided": (row.get("提供的支持") or "").strip() or None,
                        "sources": _split(row.get("来源链接")) and [row["来源链接"].strip()],
                        "tag1": _split(row.get("领域")), "tag2": _split(row.get("岗位")),
                    })
        return items
