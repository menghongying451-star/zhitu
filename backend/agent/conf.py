"""
智能体配置。优先读 Django settings，其次读环境变量，最后用默认值。

在 .env 中至少配置：
    AGENT_LLM_API_KEY=sk-xxx
其余可选：
    AGENT_LLM_BASE_URL   OpenAI 兼容接口地址（默认阿里云百炼 DashScope）
    AGENT_LLM_MODEL      对话/推理主模型（默认 qwen-plus）
    AGENT_LLM_FAST_MODEL 结构化抽取用的模型（默认与主模型相同）
    AGENT_LLM_TIMEOUT    单次请求超时秒数（默认 60）
    AGENT_SESSION_TTL    会话保存秒数（默认 7200）
"""
import os

from django.conf import settings


def _get(name, default=None):
    value = getattr(settings, name, None)
    if value is None or value == "":
        value = os.getenv(name, default)
    return value


def llm_base_url():
    return _get("AGENT_LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")


def llm_api_key():
    return _get("AGENT_LLM_API_KEY", "")


def llm_model():
    return _get("AGENT_LLM_MODEL", "qwen-plus")


def llm_fast_model():
    return _get("AGENT_LLM_FAST_MODEL", "") or llm_model()


def llm_timeout():
    return float(_get("AGENT_LLM_TIMEOUT", "60"))


def session_ttl():
    return int(_get("AGENT_SESSION_TTL", "7200"))


# 上传文件限制（与原 Dify 配置一致：15MB）
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
ALLOWED_DOC_EXT = {".pdf", ".docx", ".txt", ".md"}

# 喂给大模型的文档最大字符数（防止超长文档撑爆上下文）
MAX_DOC_CHARS = 15000
# 个人简介最大字符数
MAX_PROFILE_CHARS = 3000
# 每轮带入的历史对话条数（user+assistant 各算一条）
HISTORY_WINDOW = 8
