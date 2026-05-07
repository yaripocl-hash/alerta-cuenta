"""Shared test fixtures — isolated in-memory or temp DBs, no external calls."""

from __future__ import annotations
import os
import tempfile
from pathlib import Path

import pytest

from legal_source_kernel.db import init_db, get_db


@pytest.fixture
def tmp_db(tmp_path) -> Path:
    """Create a fresh, isolated SQLite DB for each test."""
    db_path = tmp_path / "test_kernel.db"
    init_db(db_path)
    return db_path


@pytest.fixture
def sample_law_path(tmp_path) -> Path:
    """Write a minimal law fixture to a temp file."""
    text = """# Ley de prueba

Artículo 1. Disposición general.
Texto del artículo primero para efectos de prueba.

Artículo 2. Definiciones.
Para los efectos de esta ley se entenderá por firma electrónica avanzada lo establecido aquí.

Artículo 3. Valor jurídico.
Los documentos electrónicos tendrán pleno valor legal cuando cumplan los requisitos de esta ley.

Artículo 4 bis. Regla especial.
Los organismos públicos deberán usar firma electrónica avanzada.
"""
    path = tmp_path / "ley_prueba.md"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def sample_law_yaml(tmp_path) -> Path:
    yaml_text = """title: "Ley de prueba"
source_type: "law"
jurisdiction: "Chile"
authority: "Test"
source_url: "https://example.com/ley"
date_published: "2024-01-01"
version_label: "v0.1-test"
status: "test"
trust_level: "low"
topics:
  - firma electrónica
  - documentos electrónicos
"""
    path = tmp_path / "ley_prueba.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    return path


@pytest.fixture
def sample_contract_path(tmp_path) -> Path:
    text = """# Contrato de prueba

Cláusula primera. Objeto.
Texto de ejemplo para la cláusula primera.

Cláusula segunda. Obligaciones.
El prestador se obliga a cumplir con lo acordado.

Cláusula 3. Plazos.
El plazo de ejecución será de 6 meses.

Cláusula 12.3. Evidencia y reportes.
El prestador entregará informes mensuales de cumplimiento.
"""
    path = tmp_path / "contrato_prueba.md"
    path.write_text(text, encoding="utf-8")
    return path
