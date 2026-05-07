"""Tests for segmentation patterns."""

from __future__ import annotations
import pytest
from legal_source_kernel.segment import segment_text, _ARTICLE_RE, _CLAUSE_RE


# ---------------------------------------------------------------------------
# Article detection
# ---------------------------------------------------------------------------

def test_detects_articulo_1():
    text = "Artículo 1. Disposición general.\nTexto del artículo."
    segs = segment_text(text, source_type="law")
    assert len(segs) >= 1
    assert segs[0].segment_type == "article"
    assert "artículo 1" in segs[0].locator


def test_detects_articulo_4_bis():
    text = (
        "Artículo 4. Normal.\nTexto normal.\n\n"
        "Artículo 4 bis. Regla especial.\nTexto especial."
    )
    segs = segment_text(text, source_type="law")
    locators = [s.locator for s in segs]
    assert any("bis" in (loc or "") for loc in locators)


def test_detects_articulo_uppercase():
    text = "ARTÍCULO 1. DISPOSICIÓN GENERAL.\nTexto del artículo."
    segs = segment_text(text, source_type="law")
    assert len(segs) >= 1
    assert segs[0].segment_type == "article"


def test_detects_art_abbreviated():
    text = "Art. 1. Disposición.\nTexto."
    segs = segment_text(text, source_type="law")
    assert len(segs) >= 1
    assert segs[0].segment_type == "article"


def test_detects_articulo_ordinal():
    text = "Artículo primero. Objeto.\nTexto del artículo primero."
    segs = segment_text(text, source_type="law")
    assert len(segs) >= 1
    assert "primero" in segs[0].locator


def test_multiple_articles_correct_count():
    text = """Artículo 1. Primero.
Texto del primero.

Artículo 2. Segundo.
Texto del segundo.

Artículo 3. Tercero.
Texto del tercero.
"""
    segs = segment_text(text, source_type="law")
    assert len(segs) == 3


# ---------------------------------------------------------------------------
# Clause detection
# ---------------------------------------------------------------------------

def test_detects_clausula_primera():
    text = "Cláusula primera. Objeto.\nTexto de la cláusula primera."
    segs = segment_text(text, source_type="contract")
    assert len(segs) >= 1
    assert segs[0].segment_type == "clause"
    assert "primera" in segs[0].locator


def test_detects_clausula_numeric():
    text = "Cláusula 3. Plazos.\nTexto sobre plazos."
    segs = segment_text(text, source_type="contract")
    assert len(segs) >= 1
    assert segs[0].segment_type == "clause"


def test_detects_clausula_12_3():
    text = (
        "Cláusula 12. General.\nTexto general.\n\n"
        "Cláusula 12.3. Evidencia y reportes.\nTexto sobre evidencia."
    )
    segs = segment_text(text, source_type="contract")
    locators = [s.locator for s in segs]
    assert any("12.3" in (loc or "") for loc in locators)


def test_detects_clausula_uppercase():
    text = "CLÁUSULA PRIMERA. OBJETO.\nTexto de la cláusula."
    segs = segment_text(text, source_type="contract")
    assert len(segs) >= 1
    assert segs[0].segment_type == "clause"


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def test_fallback_to_unknown_segment():
    text = "Texto sin estructura reconocible ni artículos ni cláusulas."
    segs = segment_text(text, source_type="unknown")
    assert len(segs) == 1
    assert segs[0].segment_type == "unknown"


def test_segment_preserves_text_content():
    text = "Artículo 1. Disposición.\nContenido del artículo uno."
    segs = segment_text(text, source_type="law")
    assert "Contenido del artículo uno" in segs[0].text


def test_segment_order_index_is_sequential():
    text = """Artículo 1. Primero.\nTexto uno.

Artículo 2. Segundo.\nTexto dos.

Artículo 3. Tercero.\nTexto tres.
"""
    segs = segment_text(text, source_type="law")
    assert [s.order_index for s in segs] == [0, 1, 2]
