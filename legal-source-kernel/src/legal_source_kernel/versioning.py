"""Version comparison — diff two source texts using difflib."""

from __future__ import annotations
import difflib
from pathlib import Path
from typing import Optional

from .config import get_db_path
from .db import get_db, get_source


def compare_sources(
    source_id_a: int,
    source_id_b: int,
    db_path: Optional[Path] = None,
    context_lines: int = 3,
) -> str:
    """
    Return a unified diff between the normalized texts of two sources.

    Returns an empty string if the texts are identical.
    """
    db_path = db_path or get_db_path()
    with get_db(db_path) as conn:
        src_a = get_source(conn, source_id_a)
        src_b = get_source(conn, source_id_b)

    if src_a is None:
        raise ValueError(f"Source {source_id_a} not found")
    if src_b is None:
        raise ValueError(f"Source {source_id_b} not found")

    text_a = (src_a.get("normalized_text") or "").splitlines(keepends=True)
    text_b = (src_b.get("normalized_text") or "").splitlines(keepends=True)

    label_a = f"source/{source_id_a} — {src_a['title']} ({src_a.get('version_label', '?')})"
    label_b = f"source/{source_id_b} — {src_b['title']} ({src_b.get('version_label', '?')})"

    diff = list(
        difflib.unified_diff(
            text_a,
            text_b,
            fromfile=label_a,
            tofile=label_b,
            n=context_lines,
        )
    )
    return "".join(diff)


def compare_texts(text_a: str, text_b: str, label_a: str = "a", label_b: str = "b") -> str:
    """Compare two raw text strings and return a unified diff."""
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=label_a, tofile=label_b))
    return "".join(diff)
