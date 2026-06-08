"""single_choice.py — 单项选择题问答模块"""
from __future__ import annotations

import re
from typing import List

from .llm_client import call_llm
from . import build_context


def answer(question: str, options: List[str], pages: list) -> dict:
    context = build_context(pages, max_chars=6000)

    options_text = "\n".join(f"{chr(65 + i)}. {opt}" for i, opt in enumerate(options))

    prompt = f"""你是一个文档问答助手。根据以下文档内容，回答单项选择题。
只输出一个选项字母（A/B/C/D/E/F），不要任何解释。

文档内容：
{context}

问题：{question}

选项：
{options_text}

答案（只输出字母）："""

    raw = call_llm(prompt, max_tokens=5)
    letter = _extract_single_letter(raw)

    evidence = [{"docId": p.doc_id, "fileName": p.filename, "page": p.page_num, "quote": p.full_text[:150]} for p in pages[:5]]

    confidence = 0.9 if letter else 0.3
    return {
        "modelAnswer": letter or "A",
        "evidence": evidence,
        "confidence": confidence,
    }


def _extract_single_letter(text: str) -> str:
    """从 LLM 输出中提取第一个 A-F 字母。"""
    m = re.search(r"[A-Fa-f]", text.strip())
    return m.group(0).upper() if m else ""
