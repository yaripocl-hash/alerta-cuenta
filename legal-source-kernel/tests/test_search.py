"""Tests for search functionality."""

from __future__ import annotations
import pytest

from legal_source_kernel.ingest import ingest_source
from legal_source_kernel.search import search_sources, list_all_sources


def test_search_finds_by_keyword(sample_law_path, sample_law_yaml, tmp_db):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    results = search_sources("firma electrónica avanzada", db_path=tmp_db)
    assert len(results) >= 1
    assert results[0].source_id > 0


def test_search_finds_by_title(sample_law_path, sample_law_yaml, tmp_db):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    results = search_sources("Ley de prueba", db_path=tmp_db)
    assert len(results) >= 1
    assert "prueba" in results[0].title.lower()


def test_search_returns_snippet(sample_law_path, sample_law_yaml, tmp_db):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    results = search_sources("documentos electrónicos", db_path=tmp_db)
    assert len(results) >= 1
    assert results[0].snippet  # snippet must not be empty


def test_search_no_results_for_garbage(sample_law_path, sample_law_yaml, tmp_db):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    results = search_sources("xyzzy_noresult_12345", db_path=tmp_db)
    assert results == []


def test_search_filter_by_source_type(sample_law_path, sample_law_yaml, tmp_db, sample_contract_path):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    ingest_source(sample_contract_path, db_path=tmp_db)

    law_results = search_sources("texto", source_type="law", db_path=tmp_db)
    for r in law_results:
        assert r.source_type == "law"


def test_list_all_sources(sample_law_path, sample_law_yaml, tmp_db):
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    sources = list_all_sources(db_path=tmp_db)
    assert len(sources) >= 1
    assert sources[0]["title"] == "Ley de prueba"


def test_list_sources_empty_db(tmp_db):
    sources = list_all_sources(db_path=tmp_db)
    assert sources == []


def test_search_limit(sample_law_path, sample_law_yaml, tmp_db):
    # Ingest same source multiple times to have multiple results
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)
    ingest_source(sample_law_path, sample_law_yaml, db_path=tmp_db)

    results = search_sources("Ley", limit=2, db_path=tmp_db)
    assert len(results) <= 2
