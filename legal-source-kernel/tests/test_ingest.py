"""Tests for ingestion pipeline."""

from __future__ import annotations
from pathlib import Path

import pytest

from legal_source_kernel.ingest import ingest_source
from legal_source_kernel.db import get_db, get_source, list_segments_for_source, list_audit


def test_ingest_creates_source(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    assert isinstance(source_id, int)
    assert source_id > 0

    with get_db(tmp_db) as conn:
        src = get_source(conn, source_id)

    assert src is not None
    assert src["title"] == "Ley de prueba"
    assert src["source_type"] == "law"
    assert src["jurisdiction"] == "Chile"


def test_ingest_creates_segments(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        segments = list_segments_for_source(conn, source_id)

    assert len(segments) >= 1
    locators = [s["locator"] for s in segments]
    # At least artículo 1 should be detected
    assert any("artículo 1" in (loc or "") for loc in locators)


def test_ingest_records_audit(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        entries = list_audit(conn, entity_type="source", entity_id=str(source_id))

    assert len(entries) >= 1
    assert entries[0]["action"] == "ingest_source"


def test_ingest_without_metadata_uses_file_title(sample_law_path, tmp_db):
    source_id = ingest_source(sample_law_path, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        src = get_source(conn, source_id)

    # Title should come from H1 heading in the file
    assert src is not None
    assert "Ley de prueba" in src["title"]


def test_ingest_normalizes_text(sample_law_path, tmp_db):
    source_id = ingest_source(sample_law_path, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        src = get_source(conn, source_id)

    # Normalized text should not contain Windows-style line endings
    assert src is not None
    text = src["normalized_text"] or ""
    assert "\r\n" not in text
    assert "\r" not in text


def test_ingest_stores_topics(sample_law_path, sample_law_yaml, tmp_db):
    import json
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        src = get_source(conn, source_id)

    topics = json.loads(src["topics_json"] or "[]")
    assert "firma electrónica" in topics
