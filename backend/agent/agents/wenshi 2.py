"""
文识：项目需求问答（学生端「我要揭榜 → 需求介绍 / 项目问答」）。

Dify 原流程：开始(pid, user_tone) → HTTP read-search-v2 → 角色生成器 → 回答整理 → 回复
Python 版：
  - 检索 = 数据库里该需求的完整字段 + Milvus 中该需求文档的相关片段（Milvus 挂了也能答）
  - 角色生成器合并进 system prompt
  - 支持多轮追问（带历史）；支持上传个人简介，结合简介给建议
"""
from ..base import QA_RULES, BaseAgent, ChatContext, tone_instruction
from .. import conf, documents, retrieval


class WenShiAgent(BaseAgent):
    name = "wenshi"
    title = "文识 · 项目问答"
    opening = (
        "您好，您可以向我询问本项目的需求细节。\n"
        "Tip：您也可以通过左下角上传个人介绍，以便我更了解您。"
    )
    suggestions = ["这个项目主要做什么？", "需要哪些技能？", "截止时间和人数要求是？", "企业能提供哪些支持？"]
    allow_file = True
    file_hint = "上传个人介绍 / 简历（PDF、Word、TXT）"

    def run(self, ctx: ChatContext):
        pid = ctx.inputs.get("pid") or ctx.vars.get("pid")
        req = retrieval.get_requirement(pid) if pid else None
        if not req:
            yield self.say("没有找到对应的项目需求，请从需求详情页进入后再提问。")
            return
        ctx.vars["pid"] = req.id

        # 个人简介
        if ctx.file is not None:
            text, _ = documents.read_upload(ctx.file)
            ctx.vars["profile"] = text[: conf.MAX_PROFILE_CHARS]
            if not ctx.query:
                yield self.say("已收到您的个人介绍，接下来的回答会结合您的情况。您想了解这个项目的哪些方面？")
                return
        if not ctx.query:
            yield self.say("请输入您想了解的问题。")
            return

        chunks = retrieval.vector_search(ctx.query, [req.id], top_k=5)
        context = retrieval.requirement_card(req, detail=True)
        if chunks:
            context += "\n\n【需求文档相关片段】\n" + "\n---\n".join(c["content"] for c in chunks)

        profile = ctx.vars.get("profile")
        system = (
            "# 系统任务\n你是智汇平台的“项目信息参谋”，帮助学生了解当前这个企业需求，"
            "并判断自己是否适合揭榜或加入团队。\n\n"
            f"<context>\n{context}\n</context>\n\n"
            + (f"<profile>\n学生个人简介：{profile}\n</profile>\n\n" if profile else "")
            + tone_instruction(ctx.tone)
            + "\n\n"
            + QA_RULES
        )
        yield from self.stream_answer(system, ctx)
