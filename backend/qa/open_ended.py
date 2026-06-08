"""open_ended.py — Open-ended question answering module."""
from __future__ import annotations

from typing import List

from .llm_client import call_llm
from . import build_context


def answer(question: str, pages: list) -> dict:
    """Answer an open-ended question using retrieved pages.

    Args:
        question: The question text.
        pages: List of SearchResult objects from retrieval.

    Returns:
        dict with modelAnswer, evidence, confidence.
    """
    context = build_context(pages, max_chars=8000)

    prompt = f"""根据文档内容，详细回答问题。
要求：
- 直接给出结论，不要开场白
- 用原文关键术语（不要改写成近义词）
- 分点作答（1）2）3）格式）
- 控制在 100-200 字
- 只基于文档内容，不要臆测

文档内容：
{context}

问题：{question}
回答："""

    raw = call_llm(prompt, max_tokens=400).strip()

    evidence = [{"docId": p.doc_id, "fileName": p.filename, "page": p.page_num, "quote": p.full_text[:150]} for p in pages[:5]]

    return {
        "modelAnswer": raw,
        "evidence": evidence,
        "confidence": 0.7,
    }
