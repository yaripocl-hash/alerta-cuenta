"""Custom exceptions for legal-source-kernel."""

from __future__ import annotations


class DuplicateSourceError(Exception):
    """
    Raised when an ingestion attempt would create a duplicate source.

    The existing source_id is stored so callers can decide what to do
    (skip, update, or raise to the user).
    """

    def __init__(self, existing_id: int, file_path: str, content_hash: str) -> None:
        self.existing_id = existing_id
        self.file_path = file_path
        self.content_hash = content_hash
        super().__init__(
            f"Source already ingested (id={existing_id}, file={file_path!r}). "
            "Use --force to re-ingest."
        )
