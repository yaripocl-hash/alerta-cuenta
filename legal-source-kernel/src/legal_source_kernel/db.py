"""Database layer — SQLite via sqlite3, no ORM magic."""

from __future__ import annotations
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from .models import Source, Segment, AuditEntry


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT    NOT NULL,
    source_type         TEXT    DEFAULT 'unknown',
    jurisdiction        TEXT    DEFAULT 'Chile',
    authority           TEXT,
    source_url          TEXT,
    original_path       TEXT,
    normalized_text     TEXT,
    content_hash        TEXT,
    date_published      TEXT,
    date_effective_from TEXT,
    date_effective_to   TEXT,
    version_label       TEXT,
    status              TEXT    DEFAULT 'active',
    trust_level         TEXT    DEFAULT 'medium',
    topics_json         TEXT    DEFAULT '[]',
    created_at          TEXT    DEFAULT (datetime('now')),
    updated_at          TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS segments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id      INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    segment_type   TEXT    DEFAULT 'unknown',
    locator        TEXT,
    title          TEXT,
    text           TEXT    NOT NULL,
    start_char     INTEGER,
    end_char       INTEGER,
    page           INTEGER,
    order_index    INTEGER DEFAULT 0,
    depth          INTEGER DEFAULT 0,
    parent_locator TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    action       TEXT    NOT NULL,
    entity_type  TEXT,
    entity_id    TEXT,
    details_json TEXT,
    created_at   TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sources_hash       ON sources(content_hash);
CREATE INDEX IF NOT EXISTS idx_sources_path       ON sources(original_path);
CREATE INDEX IF NOT EXISTS idx_segments_source_id ON segments(source_id);
CREATE INDEX IF NOT EXISTS idx_segments_locator   ON segments(locator);
CREATE INDEX IF NOT EXISTS idx_segments_parent    ON segments(source_id, parent_locator);
CREATE INDEX IF NOT EXISTS idx_audit_entity       ON audit_log(entity_type, entity_id);
"""

# Migrations applied to databases created before v0.2
_MIGRATIONS = [
    "ALTER TABLE sources ADD COLUMN content_hash TEXT",
    "ALTER TABLE segments ADD COLUMN depth INTEGER DEFAULT 0",
    "ALTER TABLE segments ADD COLUMN parent_locator TEXT",
]


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_db(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        _apply_migrations(conn)


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Add columns introduced in later versions; safe to run on any DB."""
    for sql in _MIGRATIONS:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # Column already exists


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def insert_source(conn: sqlite3.Connection, source: Source) -> int:
    topics_json = json.dumps(source.topics, ensure_ascii=False)
    cur = conn.execute(
        """
        INSERT INTO sources (
            title, source_type, jurisdiction, authority, source_url,
            original_path, normalized_text, content_hash,
            date_published, date_effective_from, date_effective_to,
            version_label, status, trust_level, topics_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            source.title,
            source.source_type,
            source.jurisdiction,
            source.authority,
            source.source_url,
            source.original_path,
            source.normalized_text,
            source.content_hash,
            source.date_published,
            source.date_effective_from,
            source.date_effective_to,
            source.version_label,
            source.status,
            source.trust_level,
            topics_json,
        ),
    )
    return cur.lastrowid  # type: ignore[return-value]


def find_duplicate_source(
    conn: sqlite3.Connection, original_path: str, content_hash: str
) -> Optional[int]:
    """
    Return the id of an existing source with the same path AND content hash,
    or None if no duplicate exists.

    Same path + different hash = new version, not a duplicate.
    """
    row = conn.execute(
        "SELECT id FROM sources WHERE original_path = ? AND content_hash = ?",
        (original_path, content_hash),
    ).fetchone()
    return int(row["id"]) if row else None


def get_source(conn: sqlite3.Connection, source_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM sources WHERE id = ?", (source_id,)
    ).fetchone()
    return dict(row) if row else None


def list_sources(
    conn: sqlite3.Connection,
    source_type: Optional[str] = None,
    topic: Optional[str] = None,
) -> list[dict]:
    sql = "SELECT id, title, source_type, jurisdiction, version_label, status, trust_level, topics_json, source_url, date_published FROM sources WHERE 1=1"
    params: list = []
    if source_type:
        sql += " AND source_type = ?"
        params.append(source_type)
    if topic:
        sql += " AND topics_json LIKE ?"
        params.append(f"%{topic}%")
    sql += " ORDER BY id"
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def search_sources_db(
    conn: sqlite3.Connection,
    query: str,
    source_type: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    like = f"%{query}%"
    sql = """
        SELECT id, title, source_type, version_label, source_url,
               SUBSTR(normalized_text, 1, 300) AS snippet
        FROM sources
        WHERE (title LIKE ? OR normalized_text LIKE ? OR topics_json LIKE ?)
    """
    params: list = [like, like, like]
    if source_type:
        sql += " AND source_type = ?"
        params.append(source_type)
    sql += f" LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


# ---------------------------------------------------------------------------
# Segments
# ---------------------------------------------------------------------------

def insert_segment(conn: sqlite3.Connection, segment: Segment) -> int:
    cur = conn.execute(
        """
        INSERT INTO segments (
            source_id, segment_type, locator, title, text,
            start_char, end_char, page, order_index,
            depth, parent_locator
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            segment.source_id,
            segment.segment_type,
            segment.locator,
            segment.title,
            segment.text,
            segment.start_char,
            segment.end_char,
            segment.page,
            segment.order_index,
            segment.depth,
            segment.parent_locator,
        ),
    )
    return cur.lastrowid  # type: ignore[return-value]


def get_segment_by_id(conn: sqlite3.Connection, segment_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM segments WHERE id = ?", (segment_id,)
    ).fetchone()
    return dict(row) if row else None


def get_segment_by_locator(
    conn: sqlite3.Connection, source_id: int, locator: str
) -> Optional[dict]:
    """Case-insensitive, accent-insensitive locator match."""
    # Register a custom SQLite function for accent normalization
    conn.create_function("normalize_str", 1, _normalize_str)

    row = conn.execute(
        "SELECT * FROM segments WHERE source_id = ? AND normalize_str(locator) = normalize_str(?)",
        (source_id, locator),
    ).fetchone()
    if row:
        return dict(row)
    # Fallback: partial match
    row = conn.execute(
        "SELECT * FROM segments WHERE source_id = ? AND normalize_str(locator) LIKE normalize_str(?)",
        (source_id, f"%{locator}%"),
    ).fetchone()
    return dict(row) if row else None


def _normalize_str(s: Optional[str]) -> Optional[str]:
    """Lowercase + strip accents for locale-tolerant comparisons."""
    if s is None:
        return None
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def list_segments_for_source(
    conn: sqlite3.Connection, source_id: int
) -> list[dict]:
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM segments WHERE source_id = ? ORDER BY order_index",
            (source_id,),
        ).fetchall()
    ]


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def insert_audit(conn: sqlite3.Connection, entry: AuditEntry) -> int:
    cur = conn.execute(
        """
        INSERT INTO audit_log (action, entity_type, entity_id, details_json)
        VALUES (?,?,?,?)
        """,
        (entry.action, entry.entity_type, entry.entity_id, entry.details_json),
    )
    return cur.lastrowid  # type: ignore[return-value]


def list_audit(
    conn: sqlite3.Connection,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    sql = "SELECT * FROM audit_log WHERE 1=1"
    params: list = []
    if entity_type:
        sql += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id:
        sql += " AND entity_id = ?"
        params.append(entity_id)
    sql += f" ORDER BY id DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(sql, params).fetchall()]
