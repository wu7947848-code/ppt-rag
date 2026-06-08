"""
qa/dispatcher.py — Route by questionType, time the call, attach status+latencyMs.
"""
from __future__ import annotations

import json
import time
from typing import List

from backend.qa import build_context  # noqa: F401 (re-exported for convenience)
from backend.qa import single_choice, multiple_choice, true_false, short_answer, open_ended


# SearchResult is a lightweight dataclass-like object returned by retrieval.
# Import lazily to avoid circular deps; we only need attribute access here.


def answer(task: dict, retrieval_results: list) -> dict:
    """
    Dispatch a task to the appropriate QA module.

    Parameters
    ----------
    task : dict
        Must contain keys: questionType, question.
        Optionally: options (JSON string or list).
    retrieval_results : list
        List[SearchResult] from retrieval.hybrid.query_for_retrieval.

    Returns
    -------
    dict with keys: modelAnswer, evidence, confidence, status, latencyMs
    """
    qt = task["questionType"]
    question = task["question"]

    # options may be stored as JSON string or already a list
    options_raw = task.get("options", "")
    if isinstance(options_raw, list):
        options = options_raw
    elif options_raw:
        try:
            options = json.loads(options_raw)
        except (json.JSONDecodeError, TypeError):
            options = []
    else:
        options = []

    pages = retrieval_results  # List[SearchResult]

    t0 = time.time()
    try:
        if qt == "single_choice":
            result = single_choice.answer(question, options, pages)
        elif qt == "multiple_choice":
            result = multiple_choice.answer(question, options, pages)
        elif qt == "true_false":
            result = true_false.answer(question, pages)
        elif qt == "short_answer":
            result = short_answer.answer(question, pages)
        elif qt == "open_ended":
            result = open_ended.answer(question, pages)
        else:
            result = {"modelAnswer": "", "evidence": [], "confidence": None}

        result["status"] = "success"
    except Exception as exc:  # noqa: BLE001
        result = {
            "modelAnswer": "",
            "evidence": [],
            "confidence": None,
            "status": "failed",
            "error": str(exc),
        }

    result["latencyMs"] = int((time.time() - t0) * 1000)
    return result
