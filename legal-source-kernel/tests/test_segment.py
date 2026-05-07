"""Tests for segmentation patterns."""

from __future__ import annotations
import pytest
from legal_source_kernel.segment import segment_text, _ARTICLE_RE, _CLAUSE_RE, _INCISO_LETTER_RE


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


# ---------------------------------------------------------------------------
# Sub-segmentation: incisos y letras
# ---------------------------------------------------------------------------

_ARTICLE_WITH_LETTERS = """Artículo 2. Definiciones.
Para los efectos de esta ley se entenderá por:

a) Certificado: documento que acredita la identidad del firmante.
b) Documento electrónico: representación de un hecho en formato digital.
c) Firma electrónica: mecanismo que permite identificar al autor.
d) Firma electrónica avanzada: firma certificada por un prestador acreditado.
"""

def test_sub_segments_letter_incisos():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    inciso_segs = [s for s in segs if s.depth == 1]
    assert len(inciso_segs) == 4


def test_sub_segments_locator_formato_jerarquico():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    locators = [s.locator for s in segs if s.depth == 1]
    assert "artículo 2, letra a" in locators
    assert "artículo 2, letra b" in locators
    assert "artículo 2, letra d" in locators


def test_sub_segments_parent_locator():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    sub = [s for s in segs if s.depth == 1]
    assert all(s.parent_locator == "artículo 2" for s in sub)


def test_sub_segments_depth_zero_for_articles():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    top = [s for s in segs if s.depth == 0]
    assert all(s.segment_type == "article" for s in top)


def test_sub_segments_depth_one_for_incisos():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    sub = [s for s in segs if s.depth == 1]
    assert all(s.segment_type == "inciso" for s in sub)


def test_sub_segments_order_index_sequential_across_all():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    indices = [s.order_index for s in segs]
    assert indices == list(range(len(segs)))


def test_no_sub_segments_without_list():
    text = "Artículo 1. Objeto.\nTexto sin lista de incisos."
    segs = segment_text(text, source_type="law")
    assert all(s.depth == 0 for s in segs)


def test_sub_segments_with_n_notation():
    text = """Artículo 3. Requisitos.
Son requisitos del sistema:

N° 1. Disponibilidad permanente.
N° 2. Integridad de los datos.
N° 3. Confidencialidad garantizada.
"""
    segs = segment_text(text, source_type="law")
    sub = [s for s in segs if s.depth == 1]
    assert len(sub) == 3
    assert any("n° 1" in s.locator for s in sub)


def test_sub_segments_contract_letter_incisos():
    text = """Cláusula segunda. Obligaciones del prestador.
El prestador se obliga a:

a) Desarrollar la plataforma conforme a especificaciones.
b) Proveer soporte técnico durante horario laboral.
c) Mantener confidencialidad de los datos.
"""
    segs = segment_text(text, source_type="contract")
    sub = [s for s in segs if s.depth == 1]
    assert len(sub) == 3
    locators = [s.locator for s in sub]
    assert "cláusula segunda, letra a" in locators


def test_inciso_text_preserved():
    segs = segment_text(_ARTICLE_WITH_LETTERS, source_type="law")
    letra_a = next(s for s in segs if s.locator == "artículo 2, letra a")
    assert "Certificado" in letra_a.text
