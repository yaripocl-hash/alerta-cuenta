"""
Tool contracts — high-level API functions designed to become MCP tools.

Each function here maps 1:1 to a future MCP tool.  Signatures are kept
intentionally simple so that serialization to/from JSON is straightforward.

The layer above (CLI or future MCP server) calls these functions; they
in turn coordinate db, ingest, search, cite, and versioning modules.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from .config import get_db_path
from .db import get_db, get_segment_by_id, get_segment_by_locator, list_audit
from .ingest import ingest_source as _ingest
from .search import search_sources as _search, list_all_sources
from .cite import cite_segment as _cite_seg, cite_source as _cite_src
from .versioning import compare_sources as _compare


# ---------------------------------------------------------------------------
# 1. ingest_source
# ---------------------------------------------------------------------------

def ingest_source(
    file_path: str,
    metadata_path: Optional[str] = None,
    db_path: Optional[str] = None,
    force: bool = False,
) -> dict:
    """
    Ingest a file into the kernel.

    Returns: {"source_id": int, "title": str, "segments": int, "sub_segments": int}
    Raises DuplicateSourceError if the file was already ingested (unless force=True).
    """
    _db = Path(db_path) if db_path else get_db_path()
    source_id = _ingest(
        file_path=Path(file_path),
        metadata_path=Path(metadata_path) if metadata_path else None,
        db_path=_db,
        force=force,
    )
    with get_db(_db) as conn:
        from .db import get_source, list_segments_for_source
        src = get_source(conn, source_id)
        segs = list_segments_for_source(conn, source_id)
    top = sum(1 for s in segs if s.get("depth", 0) == 0)
    return {
        "source_id": source_id,
        "title": src["title"] if src else "?",
        "segments": top,
        "sub_segments": len(segs) - top,
    }


# ---------------------------------------------------------------------------
# 2. list_sources
# ---------------------------------------------------------------------------

def list_sources(
    source_type: Optional[str] = None,
    topic: Optional[str] = None,
    db_path: Optional[str] = None,
) -> list[dict]:
    """
    List ingested sources with optional filters.

    Returns list of source summary dicts.
    """
    _db = Path(db_path) if db_path else get_db_path()
    return list_all_sources(source_type=source_type, topic=topic, db_path=_db)


# ---------------------------------------------------------------------------
# 3. search_sources
# ---------------------------------------------------------------------------

def search_sources(
    query: str,
    source_type: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[str] = None,
) -> list[dict]:
    """
    Search sources by text.

    Returns list of SearchResult-like dicts with snippet.
    """
    _db = Path(db_path) if db_path else get_db_path()
    results = _search(query, source_type=source_type, limit=limit, db_path=_db)
    return [r.model_dump() for r in results]


# ---------------------------------------------------------------------------
# 4. get_segment
# ---------------------------------------------------------------------------

def get_segment(
    source_id: int,
    locator: Optional[str] = None,
    segment_id: Optional[int] = None,
    db_path: Optional[str] = None,
) -> dict:
    """
    Retrieve a segment by ID or by (source_id + locator).

    Returns segment dict with an attached suggested citation.
    """
    _db = Path(db_path) if db_path else get_db_path()
    with get_db(_db) as conn:
        if segment_id is not None:
            seg = get_segment_by_id(conn, segment_id)
        elif locator is not None:
            seg = get_segment_by_locator(conn, source_id, locator)
        else:
            raise ValueError("Provide segment_id or locator")

    if seg is None:
        raise ValueError(f"Segment not found (source={source_id}, locator={locator!r})")

    # Attach suggested citation
    try:
        cit = _cite_seg(seg["id"], db_path=_db)
        seg["suggested_citation"] = cit.citation_text
    except Exception:
        seg["suggested_citation"] = None
    return dict(seg)


# ---------------------------------------------------------------------------
# 5. cite_segment
# ---------------------------------------------------------------------------

def cite_segment(
    segment_id: int,
    db_path: Optional[str] = None,
) -> dict:
    """
    Generate a verifiable citation for a segment.

    Returns Citation dict.
    """
    _db = Path(db_path) if db_path else get_db_path()
    cit = _cite_seg(segment_id, db_path=_db)
    return cit.model_dump()


# ---------------------------------------------------------------------------
# 6. compare_sources
# ---------------------------------------------------------------------------

def compare_sources(
    source_id_a: int,
    source_id_b: int,
    db_path: Optional[str] = None,
) -> dict:
    """
    Compare two source texts and return a unified diff.

    Returns: {"diff": str, "identical": bool}
    """
    _db = Path(db_path) if db_path else get_db_path()
    diff = _compare(source_id_a, source_id_b, db_path=_db)
    return {"diff": diff, "identical": diff == ""}


# ---------------------------------------------------------------------------
# 7. audit_trail
# ---------------------------------------------------------------------------

def audit_trail(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
    db_path: Optional[str] = None,
) -> list[dict]:
    """
    Retrieve audit log entries.

    Returns list of audit entry dicts.
    """
    _db = Path(db_path) if db_path else get_db_path()
    with get_db(_db) as conn:
        return list_audit(conn, entity_type=entity_type, entity_id=entity_id, limit=limit)
