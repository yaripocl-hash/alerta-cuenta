"""Tests for version comparison."""

from __future__ import annotations
import pytest

from legal_source_kernel.ingest import ingest_source
from legal_source_kernel.versioning import compare_texts
from legal_source_kernel import tool_contracts as tc


# ---------------------------------------------------------------------------
# compare_texts (unit, no DB)
# ---------------------------------------------------------------------------

def test_compare_texts_returns_nonempty_diff():
    text_a = "Artículo 1. Versión original.\nTexto original."
    text_b = "Artículo 1. Versión modificada.\nTexto modificado."
    diff = compare_texts(text_a, text_b, label_a="v1", label_b="v2")
    assert diff != ""
    assert "---" in diff or "+++" in diff


def test_compare_texts_identical_returns_empty():
    text = "Artículo 1. Texto igual.\nContenido."
    diff = compare_texts(text, text)
    assert diff == ""


def test_compare_texts_shows_removed_lines():
    text_a = "Línea A\nLínea B\nLínea C\n"
    text_b = "Línea A\nLínea C\n"
    diff = compare_texts(text_a, text_b)
    assert "-Línea B" in diff


def test_compare_texts_shows_added_lines():
    text_a = "Línea A\nLínea C\n"
    text_b = "Línea A\nLínea B\nLínea C\n"
    diff = compare_texts(text_a, text_b)
    assert "+Línea B" in diff


# ---------------------------------------------------------------------------
# compare_sources (integration with DB)
# ---------------------------------------------------------------------------

def test_compare_sources_different(sample_law_path, tmp_db, tmp_path):
    text_v2 = """# Ley de prueba versión 2

Artículo 1. Disposición general modificada.
Texto del artículo primero, con cambios importantes.

Artículo 2. Nuevas definiciones.
Definición actualizada de firma electrónica avanzada.
"""
    path_v2 = tmp_path / "ley_v2.md"
    path_v2.write_text(text_v2, encoding="utf-8")

    id_a = ingest_source(sample_law_path, db_path=tmp_db)
    id_b = ingest_source(path_v2, db_path=tmp_db)

    result = tc.compare_sources(id_a, id_b, db_path=str(tmp_db))
    assert not result["identical"]
    assert result["diff"] != ""


def test_compare_sources_identical(sample_law_path, tmp_db):
    id_a = ingest_source(sample_law_path, db_path=tmp_db)
    id_b = ingest_source(sample_law_path, db_path=tmp_db)
    result = tc.compare_sources(id_a, id_b, db_path=str(tmp_db))
    assert result["identical"]
    assert result["diff"] == ""


def test_compare_sources_invalid_id(tmp_db):
    with pytest.raises(ValueError):
        tc.compare_sources(999, 1000, db_path=str(tmp_db))
