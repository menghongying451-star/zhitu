"""
文档解析：替代 Dify 的「文档提取器」节点。支持 pdf / docx / txt / md。
"""
import os
import re
import uuid

from django.conf import settings

from . import conf


class DocumentError(ValueError):
    pass


def check_upload(uploaded) -> str:
    """校验上传文件，返回小写扩展名。"""
    name = uploaded.name or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in conf.ALLOWED_DOC_EXT:
        raise DocumentError(f"暂不支持 {ext or '该'} 格式，请上传 PDF / Word(docx) / TXT 文件")
    if uploaded.size and uploaded.size > conf.MAX_UPLOAD_BYTES:
        raise DocumentError("文件过大，请上传 15MB 以内的文件")
    return ext


def save_upload(uploaded, subdir: str = "agent_uploads") -> str:
    """把上传文件保存到 MEDIA_ROOT 下，返回绝对路径（发布需求时用于向量化）。"""
    ext = check_upload(uploaded)
    folder = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        for chunk in uploaded.chunks():
            f.write(chunk)
    return path


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            import fitz  # PyMuPDF

            with fitz.open(path) as doc:
                text = "\n".join(page.get_text() for page in doc)
        elif ext == ".docx":
            import docx  # python-docx

            d = docx.Document(path)
            parts = [p.text for p in d.paragraphs]
            for table in d.tables:
                for row in table.rows:
                    parts.append(" | ".join(cell.text.strip() for cell in row.cells))
            text = "\n".join(parts)
        elif ext in (".txt", ".md"):
            with open(path, "rb") as f:
                raw = f.read()
            for enc in ("utf-8", "gbk", "utf-16"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = raw.decode("utf-8", errors="ignore")
        else:
            raise DocumentError(f"不支持的文件类型: {ext}")
    except DocumentError:
        raise
    except Exception as e:
        raise DocumentError(f"文件解析失败：{e}") from e

    text = re.sub(r"[ \t　]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    if not text:
        raise DocumentError("没有从文件中读到文字内容（可能是扫描件图片），请上传可复制文字的文件")
    return text


def read_upload(uploaded, keep: bool = False):
    """
    解析上传文件。
    keep=True 时文件会保留在磁盘上并返回路径；否则解析后删除。
    返回 (text, path_or_None)
    """
    path = save_upload(uploaded)
    try:
        text = extract_text(path)
    except Exception:
        _safe_remove(path)
        raise
    if not keep:
        _safe_remove(path)
        path = None
    return text, path


def _safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
