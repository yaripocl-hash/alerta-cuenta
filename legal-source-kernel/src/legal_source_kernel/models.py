"""Pydantic models — source of truth for data shapes across the kernel."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class SourceMetadata(BaseModel):
    """Metadata that can be supplied via YAML manifest or frontmatter."""

    title: str
    source_type: str = "unknown"
    jurisdiction: str = "Chile"
    authority: Optional[str] = None
    source_url: Optional[str] = None
    date_published: Optional[str] = None
    date_effective_from: Optional[str] = None
    date_effective_to: Optional[str] = None
    version_label: Optional[str] = None
    status: str = "active"
    trust_level: str = "medium"
    topics: list[str] = Field(default_factory=list)


class Source(SourceMetadata):
    """Persisted source document."""

    id: Optional[int] = None
    original_path: Optional[str] = None
    normalized_text: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Segment(BaseModel):
    """A citable unit within a source."""

    id: Optional[int] = None
    source_id: int
    segment_type: str = "unknown"
    locator: Optional[str] = None
    title: Optional[str] = None
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    page: Optional[int] = None
    order_index: int = 0


class Citation(BaseModel):
    """A verifiable reference to a source or segment."""

    source_id: int
    segment_id: Optional[int] = None
    citation_text: str
    source_title: str
    locator: Optional[str] = None
    version_label: Optional[str] = None
    date_accessed: str
    source_url: Optional[str] = None
    confidence: str = "medium"


class SearchResult(BaseModel):
    """One row in a search result list."""

    source_id: int
    title: str
    source_type: str
    snippet: str
    version_label: Optional[str] = None
    source_url: Optional[str] = None


class AuditEntry(BaseModel):
    """One audit log record."""

    id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details_json: Optional[str] = None
    created_at: Optional[str] = None
