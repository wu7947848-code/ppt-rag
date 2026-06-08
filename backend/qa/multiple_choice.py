"""Multiple-choice QA module."""
from __future__ import annotations

import re
from typing import List

from backend.qa import build_context
from backend.qa.llm_client import call_llm


def _extract_letters(text: str) -> List[str]:
    return sorted(set(re.findall(r"[A-F]", text.upper())))


def answer(question: str, options: List[str], pages: list) -> dict:
    context = build_context(pages, max_chars=6000)

    option_lines = "\n".join(f"{chr(65+i)}. {opt}" for i, opt in enumerate(options))

    prompt_all = f"""根据文档内容，回答多项选择题。
输出所有正确选项的字母，用逗号分隔（例：A,C,D）。不要解释。

文档内容：
{context}

问题：{question}

选项：
{option_lines}

正确选项（字母，逗号分隔）："""

    raw = call_llm(prompt_all, max_tokens=20)
    letters = _extract_letters(raw)

    # Fallback: if ≤1 or ≥80% of options selected, verify per option
    if len(letters) <= 1 or len(letters) >= len(options) * 0.8:
        letters = []
        short_ctx = context[:3000]
        for i, opt in enumerate(options):
            verify_prompt = f"""文档中是否支持以下陈述？只回答"支持"或"不支持"。
文档内容：{short_ctx}
陈述：{opt}
答案："""
            resp = call_llm(verify_prompt, max_tokens=5)
            if "支持" in resp and "不支持" not in resp:
                letters.append(chr(65 + i))

    letters = sorted(set(letters))
    evidence = [{"docId": p.doc_id, "fileName": p.filename, "page": p.page_num, "quote": p.full_text[:150]} for p in pages[:5]]
    return {
        "modelAnswer": letters,
        "evidence": evidence,
        "confidence": 0.8 if letters else 0.3,
    }
