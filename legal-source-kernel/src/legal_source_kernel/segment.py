"""
Segment normalized text into citable units (articles, clauses, sections).

v0.2 adds:
- Sub-segment detection: letras (a), b)), N° notation, numbered items
- Hierarchical locators: "artículo 2, letra a"
- depth / parent_locator fields on RawSegment

Design principle: patterns must be explicit, extensible, and testable.
If segmentation fails the whole document becomes one "unknown" segment
rather than raising — segmentation quality is a separate concern from
ingestion success.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Regex patterns — top-level
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
    r"Art(?:ículo|iculo|\.)\s+"                        # Artículo / Art.
    r"(?:"
    r"\d+[\w\-]*(?:\s+(?:bis|ter|quáter|quater|[A-Z]))?"   # 1, 4 bis, 133-A
    r"|(?:" + _ORDINALS + r")"                         # primero, segundo …
    r")"
    r"(?:\°\.)?"                                       # trailing °.
    r")"
    r"(?P<rest>[^\n]*)",
    re.MULTILINE | re.IGNORECASE,
)

_CLAUSE_RE = re.compile(
    r"^"
    r"(?P<header>"
    r"Cl(?:á|a)usula\s+"                               # Cláusula / Clausula
    r"(?:"
    r"\d+(?:\.\d+)*"                                   # 1, 12.3, 1.2.3
    r"|(?:" + _ORDINALS + r")"                         # primera, segunda …
    r")"
    r")"
    r"(?P<rest>[^\n]*)",
    re.MULTILINE | re.IGNORECASE,
)

# Numbered section: "1.1" or "12.3" at start of line, followed by text
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
# Regex patterns — sub-segments (incisos)
# ---------------------------------------------------------------------------

# Letters: a) b) c) or a.- b.- at start of line
# Matches single lowercase letter followed by ) or .-
_INCISO_LETTER_RE = re.compile(
    r"^(?P<header>[a-z])(?:\)|\.-?)\s+(?=\S)",
    re.MULTILINE,
)

# N° notation: N° 1. or N.° 2. or Nº 3 at start of line
_INCISO_N_RE = re.compile(
    r"^(?P<header>N[°º]\.?\s*\d+)\.?\s+(?=\S)",
    re.MULTILINE,
)

# Numbered items with paren: 1) 2) at start of line
# Require at least one digit, exclude matches that look like section numbers (1.1)
_INCISO_NUMBER_RE = re.compile(
    r"^(?P<header>\d+)\)\s+(?=\S)",
    re.MULTILINE,
)

# Roman numerals: i) ii) iii) iv) v) vi) vii) viii) ix) x) at start of line
_INCISO_ROMAN_RE = re.compile(
    r"^(?P<header>(?:viii|vii|vi|iv|ix|xi|xii|iii|ii|i|x|v))\)\s+(?=\S)",
    re.MULTILINE | re.IGNORECASE,
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
    depth: int = 0
    parent_locator: Optional[str] = None


def segment_text(text: str, source_type: str = "unknown") -> list[RawSegment]:
    """
    Split *text* into ordered segments appropriate for *source_type*.

    Returns a flat list containing both top-level segments (depth=0) and
    their sub-segments (depth=1). Sub-segments carry parent_locator pointing
    to their parent's locator.

    Falls back gracefully: tries articles → clauses → sections → whole doc.
    """
    # --- Top-level segmentation ---
    if source_type in ("law", "regulation", "decree", "reglamento", "decreto"):
        top_segs = _apply_pattern(text, _ARTICLE_RE, "article")
    elif source_type in ("contract", "agreement", "contrato", "convenio"):
        top_segs = _apply_pattern(text, _CLAUSE_RE, "clause")
        if not top_segs:
            top_segs = _apply_pattern(text, _SECTION_RE, "section")
    else:
        top_segs = _apply_pattern(text, _ARTICLE_RE, "article")
        if not top_segs:
            top_segs = _apply_pattern(text, _CLAUSE_RE, "clause")
        if not top_segs:
            top_segs = _apply_pattern(text, _HEADING_RE, "section")

    if not top_segs:
        return [
            RawSegment(
                segment_type="unknown",
                locator="completo",
                title="Documento completo",
                text=text.strip(),
                start_char=0,
                end_char=len(text),
                order_index=0,
                depth=0,
            )
        ]

    # --- Sub-segmentation ---
    all_segs: list[RawSegment] = []
    for ts in top_segs:
        all_segs.append(ts)
        sub_segs = _get_sub_segments(ts)
        all_segs.extend(sub_segs)

    # Re-number order_index sequentially across the whole flat list
    for i, seg in enumerate(all_segs):
        seg.order_index = i

    return all_segs


# ---------------------------------------------------------------------------
# Internal helpers — top-level
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
                depth=0,
            )
        )
    return segments


# ---------------------------------------------------------------------------
# Internal helpers — sub-segmentation
# ---------------------------------------------------------------------------

def _get_sub_segments(parent: RawSegment) -> list[RawSegment]:
    """
    Detect incisos, letters, and numbered items within *parent*.

    Tries patterns in priority order. Returns the first set that produces
    results, or an empty list if nothing matches.
    """
    # Letter incisos are most common in Chilean law (a), b), c), a.-, b.-)
    sub = _apply_sub_pattern(parent.text, _INCISO_LETTER_RE, "inciso", parent)
    if sub:
        return sub

    # N° notation (N° 1., N° 2.)
    sub = _apply_sub_pattern(parent.text, _INCISO_N_RE, "inciso", parent)
    if sub:
        return sub

    # Numeric items (1), 2), 3))
    sub = _apply_sub_pattern(parent.text, _INCISO_NUMBER_RE, "inciso", parent)
    if sub:
        return sub

    return []


def _apply_sub_pattern(
    text: str,
    pattern: re.Pattern,
    seg_type: str,
    parent: RawSegment,
) -> list[RawSegment]:
    """
    Find all sub-segment matches within *text* (the parent's text).

    Returns empty list if fewer than 2 matches are found — a single
    isolated letter match is probably not a real inciso list.
    """
    matches = list(pattern.finditer(text))
    # Require at least 2 items to consider it a real list
    if len(matches) < 2:
        return []

    result: list[RawSegment] = []
    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        raw_text = text[start:end].strip()

        header = m.group("header").strip()
        label = _inciso_label(header)
        locator = f"{parent.locator}, {label}"
        title = _inciso_title(header, raw_text)

        result.append(
            RawSegment(
                segment_type=seg_type,
                locator=locator,
                title=title,
                text=raw_text,
                start_char=parent.start_char + start,
                end_char=parent.start_char + end,
                order_index=0,  # re-numbered by segment_text()
                depth=parent.depth + 1,
                parent_locator=parent.locator,
            )
        )
    return result


def _inciso_label(header: str) -> str:
    """
    Convert a raw inciso header to a readable label used in the locator.

    Examples:
        "a"   → "letra a"
        "b"   → "letra b"
        "1"   → "número 1"
        "N° 3" → "n° 3"
    """
    h = header.strip().rstrip(")").rstrip(".")
    if len(h) == 1 and h.isalpha():
        return f"letra {h.lower()}"
    if h.isdigit():
        return f"número {h}"
    # N° X or roman numerals — lowercase as-is
    return h.lower().strip()


def _inciso_title(header: str, text: str, max_len: int = 80) -> str:
    """Generate a display title from the first line of inciso text."""
    first_line = text.split("\n")[0].strip()
    if len(first_line) > max_len:
        return first_line[:max_len] + "…"
    return first_line


def _normalize_locator(header: str) -> str:
    """Lowercase and trim the header to produce a stable locator key."""
    return " ".join(header.lower().split())
