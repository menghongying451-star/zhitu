"""
智能体测试：用假的大模型跑通三个智能体的完整流程（不需要真实 API Key / Milvus）。

运行：python manage.py test agent
"""
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from agent import llm as llm_module


class FakeLLM:
    """按 system prompt 里的关键词返回固定结果。"""

    def __init__(self):
        self.calls = []

    def chat_json(self, system, user, model=None):
        self.calls.append(("json", system[:30]))
        if "企业需求信息抽取" in system:
            return {
                "title": "校园二手交易小程序开发需求",
                "brief": "开发面向大学生的二手交易微信小程序",
                "description": "1. 商品发布与搜索\n2. 在线沟通\n3. 校园身份认证",
                "finish_time": "2026年12月31日",
                "support_provided": "提供云服务器与导师指导",
                "budget": "5",
                "people_count": "3-5",
            }
        if "需求编辑助手" in system:
            draft = json.loads(user.split("【当前草稿】\n", 1)[1].split("\n\n【修改意见】", 1)[0])
            if "预算" in user:
                draft["budget"] = "30"
            return {**draft, "retag": False}
        if "标签匹配助手" in system:
            return {"tag1_ids": [62, 9999, "62"], "group_ids": [100]}
        if "岗位匹配助手" in system:
            return {"tag2_ids": [101, 5000]}
        return {}

    def stream(self, messages, model=None, temperature=0.5):
        system = messages[0]["content"]
        self.calls.append(("stream", system[:30]))
        marker = "有资料" if "<context>" in system and "校园二手交易" in system else "无资料"
        for piece in ["好的，", "这是回答（", marker, "）。"]:
            yield piece

    def chat(self, messages, **kw):
        return "ok"


@override_settings(MEDIA_ROOT="/tmp/agent_test_media")
class AgentFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from organization.models import Organization
        from user.models import OrganizationUser, Student, Tag1, Tag2, User

        Tag1.objects.create(id=62, value="软件和信息技术服务  ")
        Tag1.objects.create(id=80, value="教育")
        Tag2.objects.create(id=100, post="互联网-前端/移动开发", category="互联网", subcategory="前端/移动开发", level=1)
        Tag2.objects.create(id=101, post="互联网-前端/移动开发-前端开发", category="互联网",
                            subcategory="前端/移动开发", specialty="前端开发", parent_id=100, level=2)

        # bulk_create 跳过 Organization.save() 里的业务校验
        Organization.objects.bulk_create([Organization(id=1, name="测试科技有限公司",
                                                       organization_type="enterprise", scale="small")])
        cls.org = Organization.objects.get(id=1)
        cls.ent_user = User.objects.create(username="ent", email="ent@test.com")
        cls.org_user = OrganizationUser.objects.create(user=cls.ent_user, organization=cls.org)
        cls.stu_user = User.objects.create(username="stu", email="stu@test.com")
        cls.student = Student.objects.create(user=cls.stu_user, student_id="2024000001", school="北邮",
                                             major="智能科学与技术", grade="2024")

    def setUp(self):
        self.fake = FakeLLM()
        llm_module.set_llm(self.fake)
        self.client = APIClient()

    def tearDown(self):
        llm_module.set_llm(None)

    # ---- helpers ----
    def chat(self, user, agent, query="", conv=None, inputs=None, file=None):
        self.client.force_authenticate(user)
        data = {"query": query, "inputs": json.dumps(inputs or {})}
        if conv:
            data["conversation_id"] = conv
        if file:
            data["file"] = file
        resp = self.client.post(f"/api/v1/agent/{agent}/chat/?stream=0", data, format="multipart")
        self.assertEqual(resp.status_code, 200, resp.content)
        return resp.json()

    # ---- 填宝 ----
    def test_tianbao_publish_flow(self):
        from project.models import Requirement

        doc = SimpleUploadedFile("需求说明.txt", "校园二手交易小程序，需要前端开发，预算5万元。".encode("utf-8"))
        r1 = self.chat(self.ent_user, "tianbao", file=doc)
        conv = r1["conversation_id"]
        self.assertIn("校园二手交易小程序开发需求", r1["answer"])
        self.assertIn("软件和信息技术服务", r1["answer"])
        self.assertIn("前端开发", r1["answer"])
        self.assertIn("确认发布", r1["answer"])

        r2 = self.chat(self.ent_user, "tianbao", "预算改为30万", conv)
        self.assertIn("已更新：预算", r2["answer"])

        r3 = self.chat(self.ent_user, "tianbao", "确认发布", conv)
        self.assertIn("发布成功", r3["answer"])
        req = Requirement.objects.get(title="校园二手交易小程序开发需求")
        self.assertEqual(req.budget, "30")
        self.assertEqual(req.status, "under_review")
        self.assertEqual(req.organization_id, self.org.id)
        self.assertEqual(req.publish_people_id, self.org_user.id)
        self.assertEqual(str(req.finish_time), "2026-12-31")
        self.assertEqual(list(req.tag1.values_list("id", flat=True)), [62])
        self.assertEqual(list(req.tag2.values_list("id", flat=True)), [101])
        self.assertTrue(any(e.get("name") == "requirement_published" for e in r3["events"]))

    def test_tianbao_forbidden_for_student(self):
        self.client.force_authenticate(self.stu_user)
        resp = self.client.post("/api/v1/agent/tianbao/chat/?stream=0", {"query": "hi"}, format="json")
        self.assertEqual(resp.status_code, 403)

    # ---- 知途 ----
    def _make_requirement(self, title="校园二手交易小程序开发需求"):
        from project.models import Requirement

        req = Requirement.objects.create(
            title=title, brief="简介", description="详细", status="in_progress",
            organization=self.org, publish_people=self.org_user,
        )
        req.tag1.set([62])
        req.tag2.set([101])
        return req

    def test_zhitu_profile_confirm_favorite(self):
        from project.models import RequirementFavorite
        from read_search.models import TagMatch
        from user.models import Tag1StuMatch, Tag2StuMatch

        req = self._make_requirement()
        r0 = self.chat(self.stu_user, "zhitu", "都有哪些大类")
        conv = r0["conversation_id"]
        self.assertIn("软件和信息技术服务", r0["answer"])

        r1 = self.chat(self.stu_user, "zhitu", "我想做一个校园小程序", conv, inputs={"tone": "活泼"})
        self.assertIn("我已确认", r1["answer"])

        r2 = self.chat(self.stu_user, "zhitu", "我已确认", conv)
        self.assertIn("录入成功", r2["answer"])
        self.assertEqual(list(Tag1StuMatch.objects.filter(student=self.student).values_list("tag1_id", flat=True)), [62])
        self.assertEqual(list(Tag2StuMatch.objects.filter(student=self.student).values_list("tag2_id", flat=True)), [101])
        self.assertTrue(TagMatch.objects.filter(student_id=self.student.id, requirement_id=req.id).exists())
        self.assertIn("有资料", r2["answer"])  # 推荐时带上了候选项目

        r3 = self.chat(self.stu_user, "zhitu", "我对校园二手交易小程序开发需求感兴趣", conv)
        self.assertIn("归档成功", r3["answer"])
        self.assertTrue(RequirementFavorite.objects.filter(student=self.student, requirement=req).exists())

        r4 = self.chat(self.stu_user, "zhitu", "重新测定", conv)
        self.assertIn("重新开始", r4["answer"])

    def test_zhitu_favorite_in_new_session(self):
        """刷新页面后（新会话、方向测定阶段）直接说「我对XX感兴趣」也能收藏；对不上机会名称时仍当作方向描述。"""
        from project.models import RequirementFavorite

        req = self._make_requirement()
        r = self.chat(self.stu_user, "zhitu", "我对校园二手交易小程序开发需求感兴趣")
        self.assertIn("归档成功", r["answer"])
        self.assertTrue(RequirementFavorite.objects.filter(student=self.student, requirement=req).exists())

        r2 = self.chat(self.stu_user, "zhitu", "我对大模型应用开发感兴趣")
        self.assertNotIn("没有找到", r2["answer"])
        self.assertIn("我已确认", r2["answer"])

    # ---- 文识 ----
    def test_wenshi_answer_with_context(self):
        req = self._make_requirement()
        r = self.chat(self.stu_user, "wenshi", "这个项目需要什么技能？", inputs={"pid": req.id})
        self.assertIn("有资料", r["answer"])

    def test_wenshi_missing_pid(self):
        r = self.chat(self.stu_user, "wenshi", "你好")
        self.assertIn("没有找到对应的项目需求", r["answer"])

    # ---- SSE ----
    def test_sse_stream(self):
        req = self._make_requirement()
        self.client.force_authenticate(self.stu_user)
        resp = self.client.post("/api/v1/agent/wenshi/chat/",
                                {"query": "介绍一下", "inputs": {"pid": req.id}}, format="json")
        self.assertEqual(resp["Content-Type"], "text/event-stream; charset=utf-8")
        body = b"".join(resp.streaming_content).decode()
        events = [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]
        self.assertEqual(events[0]["type"], "meta")
        self.assertEqual(events[-1]["type"], "done")
        self.assertIn("有资料", "".join(e.get("text", "") for e in events))

    def test_meta(self):
        self.client.force_authenticate(self.stu_user)
        resp = self.client.get("/api/v1/agent/zhitu/")
        self.assertEqual(resp.json()["name"], "zhitu")
