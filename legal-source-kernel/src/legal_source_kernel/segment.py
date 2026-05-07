"""
Segment normalized text into citable units (articles, clauses, sections).

Design principle: patterns must be explicit, extensible, and testable.
If segmentation fails, the whole document becomes one "unknown" segment
rather than raising an error — segmentation quality is a separate concern
from ingestion success.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Spanish ordinals for article/clause headers (masculine and feminine)
_ORDINALS = (
    "primer[ao]?|segund[ao]?|tercer[ao]?|cuart[ao]?|quint[ao]?|sext[ao]?"
    "|séptim[ao]?|octav[ao]?|noven[ao]?|décim[ao]?"
    "|undécim[ao]?|duodécim[ao]?"
)

_ARTICLE_RE = re.compile(
    r"^"
    r"(?P<header>"
    r"Art(?:ículo|iculo|\.)\s+"                       # Artículo / Art.
    r"(?:"
    r"\d+[\w\-]*(?:\s+(?:bis|ter|quáter|quater|[A-Z]))?"  # 1, 4 bis, 133-A
    r"|(?:" + _ORDINALS + r")"                        # primero, segundo …
    r")"
    r"(?:\°\.)?"                                      # trailing °.
    r")"
    r"(?P<rest>[^\n]*)",
    re.MULTILINE | re.IGNORECASE,
)

_CLAUSE_RE = re.compile(
    r"^"
    r"(?P<header>"
    r"Cl(?:á|a)usula\s+"                              # Cláusula / Clausula
    r"(?:"
    r"\d+(?:\.\d+)*"                                  # 1, 12.3, 1.2.3
    r"|(?:" + _ORDINALS + r")"                        # primera, segunda …
    r")"
    r")"
    r"(?P<rest>[^\n]*)",
    re.MULTILINE | re.IGNORECASE,
)

# Numbered section: "1." or "1.1" or "12.3" at start of line, followed by text
_SECTION_RE = re.compile(
    r"^(?P<header>\d+(?:\.\d+)+)\.?\s+(?=\S)",
    re.MULTILINE,
)

# Markdown headings as fallback sections
_HEADING_RE = re.compile(
    r"^(?P<header>#{1,4}\s+.+)$",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

@dataclass
class RawSegment:
    segment_type: str
    locator: str
    title: str
    text: str
    start_char: int
    end_char: int
    order_index: int


def segment_text(text: str, source_type: str = "unknown") -> list[RawSegment]:
    """
    Split *text* into ordered segments appropriate for *source_type*.

    Falls back gracefully: tries articles → clauses → sections → whole doc.
    """
    if source_type in ("law", "regulation", "decree", "reglamento", "decreto"):
        segments = _apply_pattern(text, _ARTICLE_RE, "article")
    elif source_type in ("contract", "agreement", "contrato", "convenio"):
        segments = _apply_pattern(text, _CLAUSE_RE, "clause")
        if not segments:
            segments = _apply_pattern(text, _SECTION_RE, "section")
    else:
        # Try articles first; fall back to clauses; then markdown headings
        segments = _apply_pattern(text, _ARTICLE_RE, "article")
        if not segments:
            segments = _apply_pattern(text, _CLAUSE_RE, "clause")
        if not segments:
            segments = _apply_pattern(text, _HEADING_RE, "section")

    if not segments:
        # Whole document as a single unknown segment
        segments = [
            RawSegment(
                segment_type="unknown",
                locator="completo",
                title="Documento completo",
                text=text.strip(),
                start_char=0,
                end_char=len(text),
                order_index=0,
            )
        ]

    return segments


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply_pattern(
    text: str, pattern: re.Pattern, seg_type: str
) -> list[RawSegment]:
    """
    Find all matches of *pattern* and slice the text between them.
    Each slice becomes one segment whose text runs from the header
    to the start of the next header (exclusive).
    """
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    segments: list[RawSegment] = []
    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        raw_text = text[start:end].strip()

        header = m.group("header").strip()
        # Rest of the header line is part of the title
        rest = m.group("rest").strip() if "rest" in m.groupdict() else ""
        title = f"{header} {rest}".strip() if rest else header

        segments.append(
            RawSegment(
                segment_type=seg_type,
                locator=_normalize_locator(header),
                title=title,
                text=raw_text,
                start_char=start,
                end_char=end,
                order_index=idx,
            )
        )
    return segments


def _normalize_locator(header: str) -> str:
    """Lowercase and trim the header to produce a stable locator key."""
    return " ".join(header.lower().split())
