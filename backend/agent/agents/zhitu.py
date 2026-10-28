"""
知途：学生方向测定 + 项目推荐（学生端「需求总览」顶部智能体）。

Dify 原流程（简化后）：
  第一阶段（count == 0，方向测定）
    - “都有哪些大类”      → 列出全部领域
    - “介绍…”             → 介绍某个领域及相关能力
    - “我已确认”          → 写入学生 tag1/tag2 → 更新标签热度 → 提示录入成功 → 推荐项目
    - 其他输入            → 匹配 tag1/tag2 → 解释匹配结果 → 提示输入【我已确认】
  第二阶段（count > 0，项目推荐）
    - “我对XX项目感兴趣”  → 写入 project_requirementfavorite（即“我要揭榜”列表）
    - 其他输入            → 在初筛出的项目里向量检索并回答

Python 版保留同样的交互，同时修了几处问题：
  - 学生 ID 取自登录态，不再信任 URL 上的 sid；
  - 原版依赖的 tag_match 初筛表在仓库里没有任何代码写入，这里按标签重合度直接算候选项目，并同步写回 tag_match；
  - 原版 SQL 是字符串拼接（可注入），这里全部走 ORM / 参数化；
  - 支持“重新测定”，不用刷新页面。
"""
import difflib
import re

from .. import conf, documents, retrieval, taxonomy
from ..base import QA_RULES, BaseAgent, ChatContext, tone_instruction

CONFIRM_TIP = (
    "\n\n---\n您可以继续补充或修改您的想法，我会重新匹配。\n"
    "如果觉得没问题了，请输入：**我已确认**，我将录入您的方向偏好并为您推荐相关项目。"
)
FAVORITE_TIP = (
    "\n\n---\nTip：如果您已经确定了感兴趣的项目，请输入「**我对XX感兴趣**」（XX 为机会名称），"
    "我会帮您把它加入左侧「我的收藏」。想重新测定方向，请输入「重新测定」。"
)
GUIDE_TEXT = (
    "在这里，您可以进行方向测定，并查看根据测定结果为您推荐的项目。\n"
    "- 直接描述您想做的事情或感兴趣的内容（例如：我想做一个语音转文字助手）即可开始测定；\n"
    "- 想先看看都有哪些领域，请输入：**都有哪些大类**；\n"
    "- 想了解某个领域，请输入：**介绍一下XX**。\n\n"
    "Tip：完成方向测定并确认后，我才能为您推荐项目。"
)

RE_FAVORITE = re.compile(r"我对[「“\"'【\[]?(.+?)[」”\"'】\]]?(?:这个)?(?:项目|需求)?感兴趣")
RE_RESET = re.compile(r"重新(测定|测试|选择|匹配|开始)")
CATEGORY_WORDS = ("大类", "领域", "类别", "分类", "方向")


class ZhiTuAgent(BaseAgent):
    name = "zhitu"
    title = "知途 · 方向测定与项目推荐"
    opening = (
        "同学您好，请告诉我您对什么感兴趣、或者想做些什么，我会为您匹配方向并推荐相关项目。\n"
        "Tip：您也可以通过左下角上传个人介绍，帮助我更好地为您推荐。"
    )
    suggestions = ["都有哪些大类", "我想做一个语音转文字助手", "我对大模型应用开发感兴趣", "介绍一下软件和信息技术服务"]
    allow_file = True
    file_hint = "上传个人介绍 / 简历（PDF、Word、TXT）"

    def check_permission(self, user):
        if not hasattr(user, "student_profile"):
            return "该智能体仅对学生用户开放"
        return None

    # ------------------------------------------------------------------
    def run(self, ctx: ChatContext):
        v = ctx.vars
        v.setdefault("stage", "profiling")
        if ctx.inputs.get("tone"):
            v["tone"] = ctx.inputs["tone"]
        q = ctx.query.strip()

        if ctx.file is not None:
            text, _ = documents.read_upload(ctx.file)
            v["profile"] = text[: conf.MAX_PROFILE_CHARS]
            if not q:
                if v["stage"] == "profiling":
                    yield self.say("已收到您的个人介绍，我先根据它为您做一次方向匹配。\n\n")
                    yield from self._profile(ctx, "")
                else:
                    yield self.say("已收到您的个人介绍，后续推荐会结合您的情况。您想了解哪些项目？")
                return

        if not q:
            yield self.say(GUIDE_TEXT)
            return

        if RE_RESET.search(q):
            v.update(stage="profiling", interests=[], pending=None, candidates=[])
            yield self.say("好的，我们重新开始方向测定。\n\n" + GUIDE_TEXT)
            return

        if v["stage"] == "profiling":
            if "哪些" in q and any(w in q for w in CATEGORY_WORDS):
                yield from self._list_categories()
            elif "确认" in q:
                yield from self._confirm(ctx)
            elif q.startswith("介绍") or "介绍一下" in q:
                yield from self._introduce(ctx)
            else:
                yield from self._profile(ctx, q)
        else:
            m = RE_FAVORITE.search(q)
            if m:
                yield from self._favorite(ctx, m.group(1).strip())
            else:
                yield from self._recommend(ctx, q)

    # ------------------------------------------------------------------
    # 第一阶段：方向测定
    # ------------------------------------------------------------------
    def _list_categories(self):
        tags = taxonomy.tag1_list()
        body = "、".join(f"{t['id']}. {t['name']}" for t in tags)
        yield self.say(
            f"平台共有 {len(tags)} 个领域/兴趣大类可供选择：\n\n{body}\n\n"
            "您可以直接告诉我感兴趣的领域或想做的事情，我来为您匹配；"
            "也可以输入「介绍一下XX」了解某个领域。"
        )

    def _introduce(self, ctx: ChatContext):
        groups = taxonomy.tag2_groups(taxonomy.tag2_list())
        system = (
            "你是智汇平台的方向引导助手。用户想了解某个领域。请结合下面的平台标签体系，"
            "介绍该领域是做什么的、典型的实践项目方向，以及与之相关的能力/岗位（只从岗位大类表中选，不输出编号）。\n"
            f"【领域列表】{'、'.join(t['name'] for t in taxonomy.tag1_list())}\n"
            f"【岗位大类】{'、'.join(g['post'] for g in groups)}\n\n"
            + tone_instruction(ctx.tone)
            + "\n用户是大学生，但回答中不要提及这一点。最后提醒用户：如果感兴趣，可以直接描述想做的事情来进行方向测定。"
        )
        yield from self.stream_answer(system, ctx, with_history=False)

    def _profile(self, ctx: ChatContext, q: str):
        v = ctx.vars
        interests = v.setdefault("interests", [])
        parts = list(interests) + ([q] if q else [])
        desc = "\n".join(f"- {p}" for p in parts)
        if v.get("profile"):
            desc += f"\n（学生个人介绍摘要）{v['profile'][:1500]}"

        tags = taxonomy.match_tags(desc, mode="student")
        if not tags["tag1"] and not tags["tag2"]:
            # 没匹配到：如果之前有结果就保留，否则给引导
            if v.get("pending"):
                yield self.say("这次的补充我没能对应到新的方向，先保留之前的匹配结果。")
                yield self.say(CONFIRM_TIP)
                return
            system = (
                "你是智汇平台的方向引导助手。用户的输入还不足以判断兴趣方向。"
                "请简短回应用户的话（可以正常聊天或回答简单问题），然后引导用户描述想做的事情或感兴趣的内容。\n"
                f"可参考的引导信息：\n{GUIDE_TEXT}\n\n" + tone_instruction(ctx.tone)
            )
            yield from self.stream_answer(system, ctx)
            return

        if q:
            interests.append(q)
        v["pending"] = tags
        names1 = taxonomy.tag1_names(tags["tag1"])
        names2 = taxonomy.tag2_names(tags["tag2"])
        system = (
            "你是智汇平台的方向引导助手。系统已经根据用户的描述匹配出相关领域和能力/岗位。"
            "请根据匹配结果，为用户详细介绍他想做的事情：这些领域和能力分别对应需求中的哪些部分、如何组合起来实现，"
            "以及建议提升的方向。不要输出任何编号，回答中不要提及用户是大学生。\n"
            f"【用户描述】\n{desc}\n"
            f"【匹配到的领域】{'、'.join(names1) or '无'}\n"
            f"【匹配到的能力/岗位】{'、'.join(names2) or '无'}\n\n"
            + tone_instruction(ctx.tone)
            + "\n开头先用一行加粗列出匹配到的领域与能力，再展开说明，控制在 400 字以内。"
        )
        yield from self.stream_answer(system, ctx, user_content=q or "请根据我的个人介绍分析", with_history=False)
        yield self.say(CONFIRM_TIP)

    def _confirm(self, ctx: ChatContext):
        v = ctx.vars
        tags = v.get("pending")
        if not tags:
            yield self.say("还没有可以确认的方向哦。请先描述您想做的事情或感兴趣的内容，我来为您匹配。")
            return
        student = ctx.user.student_profile
        from tag_db_writer.db_writer import insert_match_from_json

        if tags["tag1"]:
            insert_match_from_json({"match_type": "tag1_student",
                                    "data": [{"student_id": student.id, "tag1_id": tags["tag1"]}]})
            taxonomy.bump_frequency("tag_1", tags["tag1"])
        if tags["tag2"]:
            insert_match_from_json({"match_type": "tag2_student",
                                    "data": [{"student_id": student.id, "tag2_id": tags["tag2"]}]})
            taxonomy.bump_frequency("tag_2", tags["tag2"])

        reqs = retrieval.candidate_requirements(tags["tag1"], tags["tag2"])
        retrieval.sync_tag_match(student.id, reqs, tags["tag1"], tags["tag2"])
        v.update(stage="recommending", candidates=[r.id for r in reqs])
        yield {"type": "action", "name": "preference_saved", "data": {"tag1": tags["tag1"], "tag2": tags["tag2"]}}
        yield self.say("感谢您的等待，您的方向偏好已经录入成功！下面为您推荐相关项目：\n\n")

        query = "；".join(v.get("interests") or []) or "推荐适合我的项目"
        yield from self._recommend(ctx, query, first=True)

    # ------------------------------------------------------------------
    # 第二阶段：项目推荐
    # ------------------------------------------------------------------
    def _candidates(self, ctx):
        from project.models import Requirement

        ids = ctx.vars.get("candidates") or []
        reqs = {r.id: r for r in Requirement.objects.filter(id__in=ids).select_related("organization")}
        return [reqs[i] for i in ids if i in reqs]

    def _recommend(self, ctx: ChatContext, query: str, first: bool = False):
        reqs = self._candidates(ctx)
        if not reqs:
            yield self.say(
                "目前平台上暂时没有与您方向匹配的开放机会。您可以：\n"
                "1. 输入「重新测定」换个方向试试；\n"
                "2. 稍后再来看看，平台会持续更新机会；\n"
                "3. 在下方「机会总览」里按标签手动筛选。"
            )
            return
        top = reqs[:8]
        chunks = retrieval.vector_search(query, [r.id for r in top], top_k=6)
        context = "\n\n".join(retrieval.requirement_card(r, detail=False) for r in top)
        if chunks:
            context += "\n\n【需求文档相关片段】\n" + "\n---\n".join(
                f"(需求编号 {c['pid']}) {c['content']}" for c in chunks
            )
        profile = ctx.vars.get("profile")
        task = (
            "请从 <context> 里挑选最适合用户的项目进行推荐：必须列出所有相关项目的准确名称，"
            "每个项目说明做什么、为什么适合用户、需要的能力。不需要提示申报资格或审核流程。"
            if first else
            "请回答用户关于这些推荐项目的问题；如果问题和项目无关，简短回答后引导用户回到项目上。"
            "提到项目时必须使用 <context> 中的准确名称。"
        )
        system = (
            "# 系统任务\n你是智汇平台的“项目信息参谋”。下面是根据学生方向偏好初筛出的企业真实需求。\n"
            f"{task}\n\n<context>\n{context}\n</context>\n\n"
            + (f"<profile>\n学生个人介绍：{profile}\n</profile>\n\n" if profile else "")
            + f"学生的兴趣描述：{'；'.join(ctx.vars.get('interests') or [])}\n\n"
            + tone_instruction(ctx.tone) + "\n\n" + QA_RULES
        )
        yield from self.stream_answer(system, ctx, user_content=query, with_history=not first)
        yield self.say(FAVORITE_TIP)

    def _favorite(self, ctx: ChatContext, name: str):
        from project.models import Requirement, RequirementFavorite

        reqs = self._candidates(ctx)
        target = _best_title_match(name, reqs)
        if target is None:  # 候选之外也找一下
            others = list(Requirement.objects.filter(status__in=retrieval.STUDENT_VISIBLE_STATUS,
                                                     title__icontains=name[:20])[:5])
            target = _best_title_match(name, others)
        if target is None:
            titles = "\n".join(f"- {r.title}" for r in reqs[:10])
            yield self.say(
                f"没有找到名为「{name}」的项目，请检查项目名称是否完整。"
                + (f"\n\n为您推荐的项目有：\n{titles}" if titles else "")
            )
            return
        RequirementFavorite.objects.get_or_create(student=ctx.user.student_profile, requirement=target)
        yield {"type": "action", "name": "requirement_favorited", "data": {"requirement_id": target.id}}
        yield self.say(
            f"「{target.title}」已为您归档成功！\n\n"
            "可以点击左侧「我的收藏」查看您收藏的机会。\n"
            "如果还想收藏其他机会，请继续输入「我对XX感兴趣」；想测定新的方向，请输入「重新测定」。"
        )


def _best_title_match(name: str, reqs):
    if not name or not reqs:
        return None
    norm = lambda s: re.sub(r"\s+", "", s or "").lower()  # noqa: E731
    n = norm(name)
    for r in reqs:
        if norm(r.title) == n:
            return r
    contains = [r for r in reqs if n in norm(r.title) or norm(r.title) in n]
    if len(contains) == 1:
        return contains[0]
    pool = contains or reqs
    best = max(pool, key=lambda r: difflib.SequenceMatcher(None, n, norm(r.title)).ratio())
    return best if difflib.SequenceMatcher(None, n, norm(best.title)).ratio() >= 0.5 else None
