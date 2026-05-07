"""Search — find sources and segments by text, type, or topic."""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from .config import get_db_path
from .db import get_db, search_sources_db, list_sources
from .models import SearchResult


def search_sources(
    query: str,
    source_type: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[Path] = None,
) -> list[SearchResult]:
    """
    Full-text search across source titles, normalized text, and topics.

    Returns ranked results (currently ranked by SQLite row order; future
    versions may add BM25 via FTS5).
    """
    db_path = db_path or get_db_path()
    with get_db(db_path) as conn:
        rows = search_sources_db(conn, query, source_type=source_type, limit=limit)

    results = []
    for row in rows:
        snippet = _extract_snippet(row.get("snippet") or "", query)
        results.append(
            SearchResult(
                source_id=row["id"],
                title=row["title"],
                source_type=row["source_type"],
                snippet=snippet,
                version_label=row.get("version_label"),
                source_url=row.get("source_url"),
            )
        )
    return results


def list_all_sources(
    source_type: Optional[str] = None,
    topic: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> list[dict]:
    db_path = db_path or get_db_path()
    with get_db(db_path) as conn:
        return list_sources(conn, source_type=source_type, topic=topic)


def _extract_snippet(text: str, query: str, window: int = 200) -> str:
    """Return a short context window around the first match of *query*."""
    lower_text = text.lower()
    lower_query = query.lower()
    pos = lower_text.find(lower_query)
    if pos == -1:
        return text[:window].strip()
    start = max(0, pos - window // 4)
    end = min(len(text), pos + len(query) + window)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet
