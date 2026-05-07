"""Tests for citation generation."""

from __future__ import annotations
from datetime import date

import pytest

from legal_source_kernel.ingest import ingest_source
from legal_source_kernel.cite import cite_segment, cite_source
from legal_source_kernel.db import get_db, list_segments_for_source


def _first_segment_id(tmp_db, source_id):
    with get_db(tmp_db) as conn:
        segs = list_segments_for_source(conn, source_id)
    return segs[0]["id"]


def test_cite_segment_contains_title(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    seg_id = _first_segment_id(tmp_db, source_id)
    cit = cite_segment(seg_id, db_path=tmp_db)
    assert "Ley de prueba" in cit.citation_text


def test_cite_segment_contains_locator(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    with get_db(tmp_db) as conn:
        segs = list_segments_for_source(conn, source_id)
    # Find a segment with a known locator
    seg = next((s for s in segs if s.get("locator")), segs[0])
    cit = cite_segment(seg["id"], db_path=tmp_db)
    assert seg["locator"] in cit.citation_text


def test_cite_segment_contains_version(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    seg_id = _first_segment_id(tmp_db, source_id)
    cit = cite_segment(seg_id, db_path=tmp_db)
    assert "v0.1-test" in cit.citation_text


def test_cite_segment_contains_date(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    seg_id = _first_segment_id(tmp_db, source_id)
    cit = cite_segment(seg_id, db_path=tmp_db)
    today = date.today().isoformat()
    assert today in cit.citation_text
    assert cit.date_accessed == today


def test_cite_segment_contains_url(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    seg_id = _first_segment_id(tmp_db, source_id)
    cit = cite_segment(seg_id, db_path=tmp_db)
    assert "example.com" in cit.citation_text


def test_cite_source(sample_law_path, sample_law_yaml, tmp_db):
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    cit = cite_source(source_id, db_path=tmp_db)
    assert "Ley de prueba" in cit.citation_text
    assert cit.segment_id is None


def test_cite_invalid_segment_raises(tmp_db):
    with pytest.raises(ValueError, match="not found"):
        cite_segment(9999, db_path=tmp_db)


def test_cite_returns_citation_model(sample_law_path, sample_law_yaml, tmp_db):
    from legal_source_kernel.models import Citation
    source_id = ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    seg_id = _first_segment_id(tmp_db, source_id)
    cit = cite_segment(seg_id, db_path=tmp_db)
    assert isinstance(cit, Citation)
    assert cit.source_id == source_id
    assert cit.segment_id == seg_id
