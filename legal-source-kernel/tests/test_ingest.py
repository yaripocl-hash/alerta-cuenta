"""Tests for ingestion pipeline."""

from __future__ import annotations
from pathlib import Path

import pytest

from legal_source_kernel.ingest import ingest_source
from legal_source_kernel.exceptions import DuplicateSourceError
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


def test_ingest_stores_content_hash(sample_law_path, tmp_db):
    source_id = ingest_source(sample_law_path, db_path=tmp_db)
    with get_db(tmp_db) as conn:
        src = get_source(conn, source_id)
    assert src["content_hash"] is not None
    assert len(src["content_hash"]) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def test_duplicate_raises_error(sample_law_path, tmp_db):
    ingest_source(sample_law_path, db_path=tmp_db)
    with pytest.raises(DuplicateSourceError) as exc_info:
        ingest_source(sample_law_path, db_path=tmp_db)
    assert exc_info.value.existing_id > 0


def test_duplicate_error_carries_existing_id(sample_law_path, tmp_db):
    first_id = ingest_source(sample_law_path, db_path=tmp_db)
    with pytest.raises(DuplicateSourceError) as exc_info:
        ingest_source(sample_law_path, db_path=tmp_db)
    assert exc_info.value.existing_id == first_id


def test_force_allows_reingest(sample_law_path, tmp_db):
    id_a = ingest_source(sample_law_path, db_path=tmp_db)
    id_b = ingest_source(sample_law_path, db_path=tmp_db, force=True)
    assert id_b != id_a  # New record created


def test_different_content_same_path_not_duplicate(tmp_db, tmp_path):
    path = tmp_path / "doc.md"
    path.write_text("# V1\nArtículo 1. Versión uno.\nTexto uno.", encoding="utf-8")
    ingest_source(path, db_path=tmp_db)

    path.write_text("# V2\nArtículo 1. Versión dos.\nTexto dos.", encoding="utf-8")
    # Different content → different hash → not a duplicate
    id_b = ingest_source(path, db_path=tmp_db)
    assert id_b > 0


# ---------------------------------------------------------------------------
# Sub-segments stored in DB
# ---------------------------------------------------------------------------

def test_ingest_with_incisos_creates_sub_segments(tmp_db, tmp_path):
    text = """# Ley con incisos

Artículo 2. Definiciones.
Para los efectos de esta ley se entenderá por:

a) Documento electrónico: representación digital.
b) Firma electrónica: mecanismo de identificación.
c) Prestador: entidad certificadora acreditada.
"""
    path = tmp_path / "ley_incisos.md"
    path.write_text(text, encoding="utf-8")
    source_id = ingest_source(path, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        segs = list_segments_for_source(conn, source_id)

    depths = [s["depth"] for s in segs]
    assert 1 in depths  # At least one sub-segment


def test_ingest_sub_segments_have_parent_locator(tmp_db, tmp_path):
    text = """# Ley

Artículo 1. Requisitos.
El sistema deberá cumplir con:

a) Disponibilidad.
b) Integridad.
c) Confidencialidad.
"""
    path = tmp_path / "ley_req.md"
    path.write_text(text, encoding="utf-8")
    source_id = ingest_source(path, db_path=tmp_db)

    with get_db(tmp_db) as conn:
        segs = list_segments_for_source(conn, source_id)

    sub_segs = [s for s in segs if s["depth"] == 1]
    assert all(s["parent_locator"] == "artículo 1" for s in sub_segs)
