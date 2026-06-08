"""
qa package — shared utilities for all QA modules.
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# SearchResult-compatible duck type expected by QA modules:
#   .filename : str
#   .page_num : int
#   .full_text: str
# ---------------------------------------------------------------------------


def build_context(pages: list, max_chars: int = 8000) -> str:
    """Concatenate retrieved pages into a single context string.

    Args:
        pages: List of SearchResult objects with .filename, .page_num, .full_text.
        max_chars: Soft cap on total character count.

    Returns:
        Multi-section string separated by horizontal rules.
    """
    parts: List[str] = []
    total = 0
    for p in pages:
        chunk = f"[文档: {p.filename} / 第{p.page_num}页]\n{p.full_text}"
        if total + len(chunk) > max_chars:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts)


__all__ = ["build_context"]
