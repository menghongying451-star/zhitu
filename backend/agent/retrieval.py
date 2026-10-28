"""
检索：数据库里的需求信息 + Milvus 向量检索（复用项目已有的 read_search / pdf_processing）。

和 Dify 版的区别：Milvus 不可用时不会整轮报错，而是退回只用数据库里的需求字段回答。
"""
import json
import logging
from typing import Iterable, List, Optional

from django.db.models import Count, Q

logger = logging.getLogger(__name__)

STUDENT_VISIBLE_STATUS = ("in_progress",)


# ---------------------------------------------------------------------------
# 需求信息
# ---------------------------------------------------------------------------
def get_requirement(pid) -> Optional["Requirement"]:  # noqa: F821
    from project.models import Requirement

    try:
        return Requirement.objects.select_related("organization").get(id=int(pid))
    except (Requirement.DoesNotExist, TypeError, ValueError):
        return None


def requirement_card(req, detail: bool = True) -> str:
    """把一条需求整理成给大模型看的文本。"""
    org = getattr(req.organization, "name", "") if getattr(req, "organization_id", None) else ""
    lines = [f"【需求】{req.title}（编号 {req.id}）"]
    if org:
        lines.append(f"发布单位：{org}")
    if req.brief:
        lines.append(f"简介：{req.brief}")
    if detail and req.description:
        lines.append(f"详细要求：{req.description[:1500]}")
    if req.finish_time:
        lines.append(f"截止时间：{req.finish_time}")
    if req.budget:
        lines.append(f"预算：{req.budget}")
    if req.people_count:
        lines.append(f"人数：{req.people_count}")
    if detail and req.support_provided:
        lines.append(f"提供给学生的支持：{req.support_provided}")
    try:
        t1 = [t.value.strip() for t in req.tag1.all()[:5]]
        t2 = [t.post for t in req.tag2.all()[:8]]
        if t1:
            lines.append(f"涉及领域：{'、'.join(t1)}")
        if t2:
            lines.append(f"涉及岗位/能力：{'、'.join(t2)}")
        if detail:
            res = [r.title for r in req.resources.all()[:8]]
            if res:
                lines.append(f"企业提供的资源：{'、'.join(res)}")
    except Exception:  # 关联表异常不影响主流程
        pass
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 向量检索
# ---------------------------------------------------------------------------
def _clean_chunk(text) -> str:
    if text is None:
        return ""
    if isinstance(text, (dict, list)):
        return json.dumps(text, ensure_ascii=False)
    s = str(text)
    try:  # 入库时用了 json.dumps(chunk)，这里还原
        v = json.loads(s)
        if isinstance(v, str):
            return v
        if isinstance(v, dict) and "content" in v:
            return str(v["content"])
    except Exception:
        pass
    return s


def vector_search(query: str, pids: Iterable, top_k: int = 5) -> List[dict]:
    pids = [int(p) for p in pids if p is not None]
    if not query or not pids:
        return []
    try:
        from read_search.read_search import search_in_milvus

        hits = search_in_milvus(query, [str(p) for p in pids], top_k=top_k)
    except Exception as e:
        logger.warning("向量检索不可用，退回数据库字段: %s", e)
        return []
    out = []
    for h in hits or []:
        content = _clean_chunk(h.get("content"))
        if content:
            out.append({"pid": h.get("pid"), "content": content, "score": h.get("score")})
    return out


def index_requirement_document(pid: int, file_path: Optional[str], text: str) -> int:
    """发布需求后把文档写入向量库，返回切块数；失败返回 0。"""
    try:
        if file_path and file_path.lower().endswith(".pdf"):
            from pdf_processing.pdf_chunk_milvus import process_pdf

            result = process_pdf(file_path, int(pid), use_cache=False)
            return int(result.get("chunks", 0) or 0)
        from pdf_processing.pdf_chunk_milvus import insert_into_milvus, split_text
        from read_search.milvus_manager import milvus_manager

        if not milvus_manager.connect():
            return 0
        chunks = split_text(text, max_char_per_chunk=300, overlap=30)
        if chunks:
            insert_into_milvus(chunks, int(pid))
        return len(chunks)
    except Exception as e:
        logger.warning("需求文档向量化失败(pid=%s): %s", pid, e)
        return 0


# ---------------------------------------------------------------------------
# 学生 → 候选需求（原 Dify 依赖 tag_match 表，但仓库里没有任何代码写这张表）
# ---------------------------------------------------------------------------
def candidate_requirements(tag1_ids: List[int], tag2_ids: List[int], limit: int = 30):
    """按标签重合度给需求排序。tag2 同时匹配其父类，避免“细分岗位不同但大类相同”漏掉。"""
    from project.models import Requirement
    from user.models import Tag2

    tag2_all = set(tag2_ids)
    tag2_all |= set(
        Tag2.objects.filter(id__in=tag2_ids, parent__isnull=False).values_list("parent_id", flat=True)
    )
    tag2_all |= set(Tag2.objects.filter(parent_id__in=tag2_ids).values_list("id", flat=True))
    if not tag1_ids and not tag2_all:
        return []
    qs = (
        Requirement.objects.filter(status__in=STUDENT_VISIBLE_STATUS)
        .filter(Q(tag1__in=tag1_ids) | Q(tag2__in=tag2_all))
        .annotate(
            s1=Count("tag1", filter=Q(tag1__in=tag1_ids), distinct=True),
            s2=Count("tag2", filter=Q(tag2__in=tag2_all), distinct=True),
        )
        .select_related("organization")
        .order_by("-s2", "-s1", "-created_at")
        .distinct()
    )
    return list(qs[:limit])


def sync_tag_match(student_id: int, reqs, tag1_ids: List[int], tag2_ids: List[int]) -> None:
    """同步写 tag_match 表，保证原有 /api/v1/search/read-search/ 接口仍然可用。"""
    try:
        from read_search.models import TagMatch

        TagMatch.objects.filter(student_id=student_id).delete()
        rows = []
        for r in reqs:
            r1 = set(r.tag1.values_list("id", flat=True)) & set(tag1_ids)
            r2 = set(r.tag2.values_list("id", flat=True)) & set(tag2_ids)
            for t in r1:
                rows.append(TagMatch(student_id=student_id, requirement_id=r.id, tag_source="tag1", tag_id=t))
            for t in r2:
                rows.append(TagMatch(student_id=student_id, requirement_id=r.id, tag_source="tag2", tag_id=t))
            if not r1 and not r2:  # 通过父类岗位匹配到的
                rows.append(TagMatch(student_id=student_id, requirement_id=r.id, tag_source="tag2", tag_id=None))
        TagMatch.objects.bulk_create(rows, ignore_conflicts=True)
        from read_search.services import search_service

        search_service.clear_student_cache(student_id)
    except Exception as e:
        logger.warning("同步 tag_match 失败: %s", e)
