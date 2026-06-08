"""Short answer QA module."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .llm_client import call_llm
from . import build_context

if TYPE_CHECKING:
    from backend.index.schema import Page


def answer(question: str, pages: list) -> dict:
    """Answer a short-answer question using retrieved pages."""
    context = build_context(pages, max_chars=4000)

    prompt = f"""根据文档内容，简短回答问题。
要求：
- 只输出答案本身，不要"答案是"、不要解释
- 如果是数字，保留单位（如 96%、100 GB）
- 如果文档中没有相关信息，只输出：文档中未提及
- 最长不超过 30 字

文档内容：
{context}

问题：{question}
答案："""

    raw = call_llm(prompt, max_tokens=50).strip()

    # Strip common redundant prefixes
    for prefix in ["答案是", "答：", "答案为", "是", "为"]:
        if raw.startswith(prefix):
            raw = raw[len(prefix):].strip()
            break

    # Truncate to 30 chars
    ans = raw[:30] if len(raw) > 30 else raw

    evidence = [{"docId": p.doc_id, "fileName": p.filename, "page": p.page_num, "quote": p.full_text[:150]} for p in pages[:5]]
    return {"modelAnswer": ans, "evidence": evidence, "confidence": 0.9}
