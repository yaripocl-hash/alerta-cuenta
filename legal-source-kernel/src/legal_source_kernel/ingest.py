"""
Ingestion pipeline — reads a file, merges metadata, normalizes, segments, persists.

Responsibilities:
1. Read raw file content (and optional YAML manifest).
2. Merge metadata from YAML / frontmatter / defaults.
3. Normalize text.
4. Segment into citable units.
5. Persist source + segments atomically.
6. Record audit entry.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import yaml

from .config import get_db_path
from .db import get_db, insert_source, insert_segment, find_duplicate_source
from .exceptions import DuplicateSourceError
from .models import Source, Segment
from .normalize import read_file, normalize_text, extract_title_from_text, compute_hash
from .segment import segment_text
from .audit import log


def ingest_source(
    file_path: Path | str,
    metadata_path: Optional[Path | str] = None,
    db_path: Optional[Path] = None,
    force: bool = False,
) -> int:
    """
    Ingest a file into the kernel.

    Returns the new source_id.

    Raises DuplicateSourceError if the same file with the same content has
    already been ingested, unless *force=True* is passed.
    """
    file_path = Path(file_path)
    db_path = db_path or get_db_path()

    # 1. Read file content and inline metadata
    raw_text, inline_meta = read_file(file_path)

    # 2. Load external YAML manifest (takes precedence over frontmatter)
    if metadata_path:
        ext_meta = _load_yaml(Path(metadata_path))
    else:
        ext_meta = {}

    meta = {**inline_meta, **ext_meta}

    # 3. Derive title fallback
    title = meta.pop("title", None) or extract_title_from_text(raw_text) or file_path.stem

    # 4. Normalize
    normalized = normalize_text(raw_text)

    # 5. Deduplication check
    content_hash = compute_hash(normalized)
    original_path = str(file_path.resolve())

    if not force:
        with get_db(db_path) as conn:
            existing_id = find_duplicate_source(conn, original_path, content_hash)
        if existing_id is not None:
            raise DuplicateSourceError(
                existing_id=existing_id,
                file_path=original_path,
                content_hash=content_hash,
            )

    # 6. Build Source model
    source = Source(
        title=title,
        source_type=meta.get("source_type", "unknown"),
        jurisdiction=meta.get("jurisdiction", "Chile"),
        authority=meta.get("authority"),
        source_url=meta.get("source_url"),
        original_path=original_path,
        normalized_text=normalized,
        content_hash=content_hash,
        date_published=meta.get("date_published"),
        date_effective_from=meta.get("date_effective_from"),
        date_effective_to=meta.get("date_effective_to"),
        version_label=meta.get("version_label"),
        status=meta.get("status", "active"),
        trust_level=meta.get("trust_level", "medium"),
        topics=meta.get("topics", []),
    )

    # 7. Segment (flat list including sub-segments)
    raw_segments = segment_text(normalized, source.source_type)

    # 8. Persist atomically
    with get_db(db_path) as conn:
        source_id = insert_source(conn, source)
        for rs in raw_segments:
            seg = Segment(
                source_id=source_id,
                segment_type=rs.segment_type,
                locator=rs.locator,
                title=rs.title,
                text=rs.text,
                start_char=rs.start_char,
                end_char=rs.end_char,
                order_index=rs.order_index,
                depth=rs.depth,
                parent_locator=rs.parent_locator,
            )
            insert_segment(conn, seg)

        top_count = sum(1 for rs in raw_segments if rs.depth == 0)
        sub_count = len(raw_segments) - top_count
        log(
            conn,
            action="ingest_source",
            entity_type="source",
            entity_id=str(source_id),
            details={
                "file": str(file_path),
                "title": title,
                "segments": top_count,
                "sub_segments": sub_count,
                "source_type": source.source_type,
                "content_hash": content_hash,
            },
        )

    return source_id


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return {}
    # Serialize dates to ISO strings for uniform handling
    result = {}
    for k, v in data.items():
        if hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result
