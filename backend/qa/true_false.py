"""true_false.py — 判断题问答模块"""
from __future__ import annotations

from typing import List

from .llm_client import call_llm
from . import build_context


def answer(question: str, pages: list) -> dict:
    """
    判断题：根据文档内容判断陈述是否正确。
    返回 ✅ 或 ❌，无法判断时保守选 ❌。
    """
    context = build_context(pages, max_chars=4000)

    prompt = f"""根据文档内容，判断以下陈述是否正确。
只输出 ✅ 或 ❌，不要任何解释。

文档内容：
{context}

陈述：{question}

判断（✅ 或 ❌）："""

    raw = call_llm(prompt, max_tokens=5)

    # 强制映射到 ✅ / ❌
    if "✅" in raw or any(w in raw for w in ["正确", "对", "true", "True", "TRUE", "是", "支持", "✓"]):
        result = "✅"
    elif "❌" in raw or any(w in raw for w in ["错误", "错", "false", "False", "FALSE", "否", "不", "×"]):
        result = "❌"
    else:
        result = "❌"  # 无法判断时保守选 ❌

    evidence = [{"docId": p.doc_id, "fileName": p.filename, "page": p.page_num, "quote": p.full_text[:150]} for p in pages[:5]]

    return {
        "modelAnswer": result,
        "evidence": evidence,
        "confidence": 0.85,
    }
