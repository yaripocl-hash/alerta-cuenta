"""Audit logging — every relevant action is recorded here."""

from __future__ import annotations
import json
import sqlite3
from typing import Any, Optional

from .db import insert_audit
from .models import AuditEntry


def log(
    conn: sqlite3.Connection,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Append one audit entry. Never raises — audit failure must not block operations."""
    try:
        entry = AuditEntry(
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details_json=json.dumps(details, ensure_ascii=False) if details else None,
        )
        insert_audit(conn, entry)
    except Exception:
        pass  # audit is best-effort; never propagate
