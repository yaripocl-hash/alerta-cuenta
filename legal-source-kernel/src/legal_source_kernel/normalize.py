"""Text normalization — convert raw input to clean, consistent Markdown."""

from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

try:
    import frontmatter as fm
    HAS_FRONTMATTER = True
except ImportError:
    HAS_FRONTMATTER = False


def read_file(path: Path) -> tuple[str, dict]:
    """
    Read a file and return (text_content, metadata_dict).

    For .md / .txt: strip YAML frontmatter if present.
    For .pdf: attempt pypdf extraction (optional dependency).
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    raw = path.read_text(encoding="utf-8")
    if HAS_FRONTMATTER and suffix in (".md", ".txt"):
        post = fm.loads(raw)
        return post.content, dict(post.metadata)
    return raw, {}


def _read_pdf(path: Path) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError(
            "pypdf is required for PDF ingestion: pip install legal-source-kernel[pdf]"
        )
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages), {}


def normalize_text(raw: str) -> str:
    """
    Produce a clean, canonical Markdown string from raw text.

    - Normalize line endings to LF
    - Collapse runs of blank lines to at most two
    - Trim trailing whitespace from every line
    - Strip leading/trailing whitespace from the whole document
    """
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    collapsed = _collapse_blank_lines(lines)
    return "\n".join(collapsed).strip()


def _collapse_blank_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return result


def compute_hash(text: str) -> str:
    """Return a SHA-256 hex digest of the normalized text (UTF-8 encoded)."""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_title_from_text(text: str) -> Optional[str]:
    """Best-effort: return the first H1 heading or the first non-blank line."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped:
            return stripped[:120]
    return None
