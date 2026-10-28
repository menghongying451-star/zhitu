"""
填宝：企业对话式发布需求（企业端「需求管理 → 对话式发布」）。

Dify 原流程：
  上传文件 → 文档提取器 → 抽取 13 个字段 → 匹配领域 tag1 → 匹配岗位 tag2 → 展示给企业
  企业继续输入修改意见 → 重新抽取
  输入「确认发布」 → INSERT project_requirement → 查回 pid → 写 tag1/tag2 → 文档向量化

Python 版：
  - 组织/发布人取自登录态（原版通过 URL 参数传，可伪造）；
  - 修改意见在“当前草稿”上增量修改，而不是每次从原文重新抽取，改了什么就是什么；
  - 发布走 ORM（原版是字符串拼接 SQL，标题里有单引号就会报错且可注入），
    直接拿到新需求 id，不再“按标题反查 pid”；
  - 发布状态与表单发布一致，默认进入「审核中」；
  - 上传的原始文件会作为需求附件保存，并写入向量库供「文识」问答使用；
  - 没有文件时也可以直接用文字描述需求。
"""
import datetime
import json
import os
import re

from django.db import transaction

from .. import conf, documents, retrieval, taxonomy
from ..base import BaseAgent, ChatContext

PUBLISH_STATUS = os.getenv("AGENT_PUBLISH_STATUS", "under_review")

FIELDS = [
    ("title", "需求名称"),
    ("brief", "简要介绍"),
    ("description", "详细要求"),
    ("finish_time", "截止时间"),
    ("support_provided", "给学生的支持"),
    ("budget", "预算（万元）"),
    ("people_count", "人数"),
]
PENDING = "待确认"

EXTRACT_RULES = f"""字段规则：
- title 需求名称：需求的核心名称，如“智能客服系统开发需求”；
- brief 简要介绍：50 字以内的概括；
- description 详细要求：具体功能、约束、交付标准等，尽量完整保留原文要点，可用换行分条；
- finish_time 截止时间：格式 YYYY-MM-DD；原文是时间段时取结束日期；
- support_provided 给学生的支持：培训、技术指导、设备、证明、实践机会、素材等；
- budget 预算：单位万元，只填数字或范围，如 "50"、"80-120"；
- people_count 人数：数字或范围，如 "5"、"3-8"。
任何字段在资料中没有信息时填 "{PENDING}"。不要编造资料中没有的信息。
输出 JSON：{{{", ".join(f'"{k}": "..."' for k, _ in FIELDS)}}}"""

CONFIRM_TIP = (
    "\n\n---\n如果无需更改，请输入：**确认发布**\n"
    "如需修改，直接告诉我即可（例如：把预算改为 30 万、截止时间延后到 12 月底、领域加上教育）。"
)


class TianBaoAgent(BaseAgent):
    name = "tianbao"
    title = "填宝 · 对话式发布需求"
    opening = (
        "您好，请上传您的需求文档（PDF / Word / TXT），我会自动帮您整理成平台需求；"
        "也可以直接用文字描述您的需求。如果有需要更改的地方，随时补充说明。"
    )
    suggestions = []
    allow_file = True
    file_hint = "上传需求文档（PDF、Word、TXT）"

    def check_permission(self, user):
        if not hasattr(user, "organization_profile"):
            return "该智能体仅对企业/组织用户开放"
        return None

    # ------------------------------------------------------------------
    def run(self, ctx: ChatContext):
        v = ctx.vars
        q = ctx.query.strip()

        if ctx.file is not None:
            text, path = documents.read_upload(ctx.file, keep=True)
            _remove(v.get("file_path"))
            v.update(doc_text=text[: conf.MAX_DOC_CHARS], file_path=path,
                     file_name=os.path.basename(ctx.file.name), notes=[q] if q else [])
            yield self.say(f"已收到文件《{v['file_name']}》，正在分析，请稍等……\n\n")
            yield from self._build_draft(ctx)
            return

        draft = v.get("draft")
        if not draft:
            if len(q) < 15:
                yield self.say("请先上传需求文档，或者用一段文字描述您的需求（做什么、要求、时间、预算、人数等）。")
                return
            v.update(doc_text=q[: conf.MAX_DOC_CHARS], notes=[])
            yield self.say("好的，正在根据您的描述整理需求，请稍等……\n\n")
            yield from self._build_draft(ctx)
            return

        if "确认" in q and len(q) <= 12 and not re.search(r"(不|别|没|未)确认", q):
            yield from self._publish(ctx)
            return
        if re.search(r"重新(开始|上传|填写)|清空", q):
            _remove(v.get("file_path"))
            ctx.state["vars"] = {}
            yield self.say("已清空当前草稿，请重新上传文档或描述需求。")
            return
        yield from self._revise(ctx, q)

    # ------------------------------------------------------------------
    def _build_draft(self, ctx: ChatContext):
        v = ctx.vars
        notes = "\n".join(v.get("notes") or []) or "无"
        today = datetime.date.today().isoformat()
        system = f"你是企业需求信息抽取助手。今天是 {today}。从需求资料中抽取字段。\n{EXTRACT_RULES}"
        user = f"【需求资料】\n{v['doc_text']}\n\n【企业补充说明（优先级高于资料）】\n{notes}"
        draft = _normalize(self.llm.chat_json(system, user))
        v["draft"] = draft
        yield self.say(f"**需求名称：** {draft['title']}\n\n**简要介绍：** {draft['brief']}\n\n正在进行领域与岗位分析……\n\n")
        v["tags"] = taxonomy.match_tags(_tag_text(draft), mode="requirement")
        yield self.say(self._render(draft, v["tags"]) + CONFIRM_TIP)

    def _revise(self, ctx: ChatContext, q: str):
        v = ctx.vars
        old = v["draft"]
        tags = v.get("tags") or {"tag1": [], "tag2": []}
        today = datetime.date.today().isoformat()
        system = (
            f"你是企业需求编辑助手。今天是 {today}。下面是当前的需求草稿（JSON）和企业的修改意见，"
            "请按修改意见更新草稿：只改企业要求修改的内容，其余字段保持原样；"
            "如果修改意见里补充了新信息，合并进对应字段。\n"
            f"{EXTRACT_RULES}\n"
            "另外输出 retag 字段（true/false）：修改意见涉及领域、岗位、方向、技能，或者需求内容发生了实质变化时为 true。\n"
            "如果企业的话不是修改意见（例如提问），在 reply 字段里用一两句话回答，其余字段保持原样。"
        )
        user = f"【当前草稿】\n{json.dumps(old, ensure_ascii=False)}\n\n【修改意见】\n{q}"
        result = self.llm.chat_json(system, user)
        new = _normalize({k: result.get(k, old.get(k)) for k, _ in FIELDS})
        changed = [label for k, label in FIELDS if new[k] != old.get(k)]
        v["draft"] = new
        v.setdefault("notes", []).append(q)
        if result.get("retag") or any(k in changed for k in ("需求名称", "详细要求")):
            yield self.say("正在重新分析领域与岗位……\n\n")
            tags = taxonomy.match_tags(_tag_text(new) + f"\n企业补充：{q}", mode="requirement")
            v["tags"] = tags
        reply = (result.get("reply") or "").strip()
        if reply and not changed:
            yield self.say(reply + "\n\n")
        elif changed:
            yield self.say(f"已更新：{'、'.join(changed)}。\n\n")
        else:
            yield self.say("没有识别到需要修改的内容，当前草稿如下：\n\n")
        yield self.say(self._render(new, tags) + CONFIRM_TIP)

    def _render(self, d: dict, tags: dict) -> str:
        names1 = taxonomy.tag1_names(tags.get("tag1", []))
        names2 = taxonomy.tag2_names(tags.get("tag2", []))
        lines = ["### 需求草稿"]
        for k, label in FIELDS:
            val = d.get(k) or PENDING
            if k == "description":
                lines.append(f"**{label}：**\n{val}")
            else:
                lines.append(f"**{label}：** {val}")
        lines.append(f"**涉及领域：** {'、'.join(names1) or PENDING}")
        lines.append(f"**涉及岗位：** {'、'.join(names2) or PENDING}")
        missing = [label for k, label in FIELDS if d.get(k) == PENDING]
        if missing:
            lines.append(f"\n> 以下信息资料中没有提到：{'、'.join(missing)}，可以直接告诉我补充。")
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    def _publish(self, ctx: ChatContext):
        from project.models import Requirement

        v = ctx.vars
        d, tags = v["draft"], v.get("tags") or {"tag1": [], "tag2": []}
        must = [label for k, label in FIELDS[:3] if not d.get(k) or d[k] == PENDING]
        if must:
            yield self.say(f"发布前还需要补充：{'、'.join(must)}。请直接告诉我对应内容。")
            return

        org_user = ctx.user.organization_profile
        yield self.say("正在发布，请稍候……\n\n")
        with transaction.atomic():
            req = Requirement.objects.create(
                title=d["title"][:255],
                brief=d["brief"][:255],
                description=d["description"],
                status=PUBLISH_STATUS,
                organization=org_user.organization,
                publish_people=org_user,
                finish_time=_parse_date(d.get("finish_time")),
                budget=_nullable(d.get("budget")),
                people_count=_nullable(d.get("people_count")),
                support_provided=_nullable(d.get("support_provided")),
            )
            if tags.get("tag1"):
                req.tag1.set(tags["tag1"])
            if tags.get("tag2"):
                req.tag2.set(tags["tag2"])
        taxonomy.bump_frequency("tag_1", tags.get("tag1"))
        taxonomy.bump_frequency("tag_2", tags.get("tag2"))

        attached = _attach_file(req, v.get("file_path"), v.get("file_name"))
        chunks = retrieval.index_requirement_document(
            req.id, v.get("file_path"),
            v.get("doc_text", "") + "\n" + d["description"],
        )
        _remove(v.get("file_path"))
        ctx.state["vars"] = {}

        yield {"type": "action", "name": "requirement_published", "data": {"requirement_id": req.id}}
        status_text = dict(Requirement.STATUS_CHOICES).get(req.status, req.status)
        extra = []
        if attached:
            extra.append("原始文档已作为需求附件保存")
        if chunks:
            extra.append("文档已录入知识库，学生可以通过智能体询问需求细节")
        yield self.say(
            f"需求「{req.title}」发布成功！当前状态：{status_text}。\n"
            + ("".join(f"\n- {e}" for e in extra) + "\n" if extra else "")
            + "\n感谢您使用智汇平台，您可以在「需求管理」中查看和编辑该需求，也可以继续上传新的需求文档。"
        )


# ----------------------------------------------------------------------
def _normalize(d: dict) -> dict:
    out = {}
    for k, _ in FIELDS:
        val = d.get(k)
        if isinstance(val, (list, tuple)):
            val = "\n".join(str(x) for x in val)
        val = str(val).strip() if val is not None else ""
        out[k] = val or PENDING
    out["brief"] = out["brief"][:120]
    return out


def _tag_text(d: dict) -> str:
    return f"需求名称：{d['title']}\n简介：{d['brief']}\n详细要求：{d['description'][:3000]}"


def _nullable(val):
    return None if not val or val == PENDING else str(val)[:2000]


def _parse_date(val):
    if not val:
        return None
    m = re.search(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})", str(val))
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _attach_file(req, path, name) -> bool:
    """复用表单发布的附件逻辑，把原始文档挂到需求的「文件信息」里。"""
    if not path or not os.path.exists(path):
        return False
    try:
        from django.core.files import File as DjangoFile
        from project.serializers import RequirementCreateSerializer

        with open(path, "rb") as f:
            django_file = DjangoFile(f, name=name or os.path.basename(path))
            ids = RequirementCreateSerializer(context={})._handle_file_upload(req, [django_file])
        if ids:
            req.files.add(*ids)
        return bool(ids)
    except Exception:
        return False


def _remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
