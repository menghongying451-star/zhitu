"""
标签体系：兴趣/领域标签 tag_1 与 能力/岗位标签 tag_2。

原 Dify 版把 695 条岗位表整段贴进 prompt，又用 3~4 个 LLM 节点反复“提取 ID”。
这里改为：
  1. 标签直接从数据库读取（新增标签无需改 prompt）；
  2. 两段式匹配：先选领域 + 岗位大类（113 个），再在大类里选细分岗位，prompt 小一个数量级；
  3. 模型返回的 ID 全部在代码里校验，非法 ID 直接丢弃，不再需要“二次提取 ID”的节点。
"""
import logging
from typing import Dict, List

from django.db import connection

from .llm import get_llm

logger = logging.getLogger(__name__)

MAX_TAG1 = 5
MAX_TAG2 = 10


# ---------------------------------------------------------------------------
# 读取标签
# ---------------------------------------------------------------------------
def tag1_list() -> List[dict]:
    from user.models import Tag1

    return [{"id": t.id, "name": (t.value or "").strip()} for t in Tag1.objects.all().order_by("id")]


def tag2_list() -> List[dict]:
    from user.models import Tag2

    rows = Tag2.objects.all().order_by("id").values(
        "id", "post", "category", "subcategory", "specialty", "parent_id", "level"
    )
    return [dict(r) for r in rows]


def tag2_groups(tags2: List[dict]) -> List[dict]:
    """岗位大类（没有 parent 的条目）。"""
    return [t for t in tags2 if not t["parent_id"]]


def tag1_names(ids: List[int]) -> List[str]:
    m = {t["id"]: t["name"] for t in tag1_list()}
    return [m[i] for i in ids if i in m]


def tag2_names(ids: List[int]) -> List[str]:
    out = []
    m = {t["id"]: t for t in tag2_list()}
    for i in ids:
        t = m.get(i)
        if t:
            out.append(t["post"])
    return out


def _clean_ids(raw, valid: set, limit: int) -> List[int]:
    """把模型输出的 ID 列表清洗为合法、去重、限长的整数列表。"""
    if raw is None:
        return []
    if isinstance(raw, (int, str)):
        raw = str(raw).replace("，", ",").split(",")
    out = []
    for x in raw:
        try:
            v = int(str(x).strip())
        except (TypeError, ValueError):
            continue
        if v in valid and v not in out:
            out.append(v)
    return out[:limit]


# ---------------------------------------------------------------------------
# 匹配
# ---------------------------------------------------------------------------
RULES = {
    # 企业需求（填宝）：只匹配核心，避免过度匹配
    "requirement": (
        "1. 优先匹配需求主要业务/活动对应的领域与岗位，按“核心优先”排序；\n"
        "2. 次要的辅助工具使用（如用 Excel 统计数据）不单独匹配；\n"
        "3. 需求涉及多个领域时按业务本质排序，例如“农产品线上销售”→ 农业、零售；\n"
        "4. 文档内容与企业补充说明冲突时，以补充说明为准；\n"
        "5. 至少输出 1 个领域和 1 个岗位，禁止输出空列表。"
    ),
    # 学生方向（知途）：尽量覆盖，便于推荐
    "student": (
        "1. 匹配学生兴趣/能力/愿望涉及的全部领域与岗位，按相关度排序；\n"
        "2. 配套活动也要匹配（如“电商运营+技术培训”→ 零售、教育）；\n"
        "3. 描述较模糊时可合理联想（如“做个语音转文字助手”→ 软件和信息技术服务、人工智能-语音）；\n"
        "4. 学生后来的补充以最新说法为准；\n"
        "5. 实在无法判断时输出空列表，不要乱填。"
    ),
}


def match_tags(text: str, mode: str = "requirement") -> Dict[str, List[int]]:
    """
    根据文本匹配 tag1（领域/兴趣）和 tag2（能力/岗位）。
    返回 {"tag1": [...], "tag2": [...]}
    """
    llm = get_llm()
    tags1 = tag1_list()
    tags2 = tag2_list()
    groups = tag2_groups(tags2)
    rules = RULES.get(mode, RULES["requirement"])

    # ---- 第一段：领域 + 岗位大类 ----
    tag1_table = "、".join(f"{t['id']}={t['name']}" for t in tags1)
    group_table = "、".join(f"{g['id']}={g['post']}" for g in groups)
    system = (
        "你是标签匹配助手，负责把一段描述匹配到平台固定的标签体系上。\n"
        f"【领域/兴趣标签 tag1】{tag1_table}\n"
        f"【岗位大类 group】{group_table}\n"
        f"【匹配规则】\n{rules}\n"
        f"输出格式：{{\"tag1_ids\": [最多{MAX_TAG1}个 tag1 编号], \"group_ids\": [最多6个岗位大类编号]}}，"
        "只能使用上表中出现的编号。"
    )
    try:
        r1 = llm.chat_json(system, f"待匹配的描述：\n{text}")
    except Exception as e:
        logger.exception("标签匹配第一段失败: %s", e)
        return {"tag1": [], "tag2": []}

    tag1_ids = _clean_ids(r1.get("tag1_ids"), {t["id"] for t in tags1}, MAX_TAG1)
    group_ids = _clean_ids(r1.get("group_ids"), {g["id"] for g in groups}, 6)
    if not group_ids:
        return {"tag1": tag1_ids, "tag2": []}

    # ---- 第二段：在选中的大类下选细分岗位 ----
    children = [t for t in tags2 if t["parent_id"] in group_ids]
    if not children:
        return {"tag1": tag1_ids, "tag2": group_ids[:MAX_TAG2]}
    lines = []
    for gid in group_ids:
        g = next(x for x in groups if x["id"] == gid)
        subs = "、".join(f"{c['id']}={c['specialty'] or c['post']}" for c in children if c["parent_id"] == gid)
        lines.append(f"[{gid}={g['post']}] {subs}")
    system2 = (
        "你是岗位匹配助手。下面是若干岗位大类及其细分岗位（编号=名称）：\n"
        + "\n".join(lines)
        + f"\n【匹配规则】\n{rules}\n"
        f"请选出最相关的细分岗位；某个大类下没有合适的细分岗位时，可以直接输出该大类编号。\n"
        f"输出格式：{{\"tag2_ids\": [最多{MAX_TAG2}个编号]}}"
    )
    valid2 = {c["id"] for c in children} | set(group_ids)
    try:
        r2 = llm.chat_json(system2, f"待匹配的描述：\n{text}")
        tag2_ids = _clean_ids(r2.get("tag2_ids"), valid2, MAX_TAG2)
    except Exception as e:
        logger.exception("标签匹配第二段失败: %s", e)
        tag2_ids = []
    if not tag2_ids:
        tag2_ids = group_ids[:MAX_TAG2]
    return {"tag1": tag1_ids, "tag2": tag2_ids}


# ---------------------------------------------------------------------------
# 热度统计（原 Dify：UPDATE tag_x SET frequency = frequency + 1）
# ---------------------------------------------------------------------------
_freq_cols: Dict[str, bool] = {}


def _has_frequency(table: str) -> bool:
    if table not in _freq_cols:
        try:
            with connection.cursor() as cur:
                cols = [c.name for c in connection.introspection.get_table_description(cur, table)]
            _freq_cols[table] = "frequency" in cols
        except Exception:
            _freq_cols[table] = False
    return _freq_cols[table]


def bump_frequency(table: str, ids: List[int]) -> None:
    if table not in ("tag_1", "tag_2") or not ids or not _has_frequency(table):
        return
    placeholders = ",".join(["%s"] * len(ids))
    sql = (
        f"UPDATE {table} SET frequency = CAST(COALESCE(NULLIF(frequency, ''), '0') AS UNSIGNED) + 1 "
        f"WHERE id IN ({placeholders})"
    )
    try:
        with connection.cursor() as cur:
            cur.execute(sql, [int(i) for i in ids])
    except Exception as e:  # 统计失败不影响主流程
        logger.warning("更新标签热度失败: %s", e)
