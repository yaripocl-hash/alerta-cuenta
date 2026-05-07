"""Citation generation — produce verifiable, human-readable references."""

from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Optional

from .config import get_db_path
from .db import get_db, get_segment_by_id, get_source
from .models import Citation


def cite_segment(
    segment_id: int,
    db_path: Optional[Path] = None,
) -> Citation:
    """
    Generate a citation for a given segment.

    Format:
        [Título], [locator], versión [version_label], consultado [YYYY-MM-DD].
        Fuente: [source_url]
    """
    db_path = db_path or get_db_path()
    with get_db(db_path) as conn:
        seg = get_segment_by_id(conn, segment_id)
        if seg is None:
            raise ValueError(f"Segment {segment_id} not found")
        src = get_source(conn, seg["source_id"])
        if src is None:
            raise ValueError(f"Source {seg['source_id']} not found")

    today = date.today().isoformat()
    locator = seg.get("locator") or "sin locator"
    version = src.get("version_label") or "sin versión"
    title = src["title"]
    url = src.get("source_url") or "sin URL"

    citation_text = (
        f"{title}, {locator}, versión {version}, consultado {today}. "
        f"Fuente: {url}"
    )

    return Citation(
        source_id=src["id"],
        segment_id=segment_id,
        citation_text=citation_text,
        source_title=title,
        locator=locator,
        version_label=version,
        date_accessed=today,
        source_url=src.get("source_url"),
        confidence="manual" if src.get("trust_level") == "high" else "medium",
    )


def cite_source(
    source_id: int,
    db_path: Optional[Path] = None,
) -> Citation:
    """Generate a citation for an entire source (no specific segment)."""
    db_path = db_path or get_db_path()
    with get_db(db_path) as conn:
        src = get_source(conn, source_id)
        if src is None:
            raise ValueError(f"Source {source_id} not found")

    today = date.today().isoformat()
    version = src.get("version_label") or "sin versión"
    title = src["title"]
    url = src.get("source_url") or "sin URL"

    citation_text = (
        f"{title}, versión {version}, consultado {today}. "
        f"Fuente: {url}"
    )

    return Citation(
        source_id=source_id,
        citation_text=citation_text,
        source_title=title,
        version_label=version,
        date_accessed=today,
        source_url=src.get("source_url"),
        confidence="medium",
    )
