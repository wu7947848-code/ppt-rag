"""
hybrid.py — BM25 retrieval → [optional query expand] → [optional LLM rerank].
"""
from __future__ import annotations

import logging
from typing import List, Optional

from backend.index.bm25_store import bm25_store
import backend.config as config

logger = logging.getLogger(__name__)


class SearchResult:
    def __init__(
        self,
        doc_id: str,
        filename: str,
        page_num: int,
        title: str,
        full_text: str,
        score: float = 0.0,
        is_divider: bool = False,
    ):
        self.doc_id = doc_id
        self.filename = filename
        self.page_num = page_num
        self.title = title
        self.full_text = full_text
        self.score = score
        self.is_divider = is_divider

    def __repr__(self) -> str:
        return f"SearchResult(doc_id={self.doc_id!r}, page_num={self.page_num}, score={self.score:.4f})"


def _bm25_result_to_obj(r) -> SearchResult:
    return SearchResult(
        doc_id=r.doc_id, filename=r.filename, page_num=r.page_num,
        title=r.title, full_text=r.full_text, score=r.score,
        is_divider=r.is_divider,
    )


def query_for_retrieval(
    question: str,
    options: Optional[List[str]] = None,
    top_k_final: int = 5,
) -> List[SearchResult]:
    """BM25 retrieval → [LLM rerank] → top-k."""

    # Build query text
    query_text = question
    if config.QUERY_EXPAND_ENABLED:
        from backend.retrieval.query_expander import expand_query
        query_text = expand_query(question, options)
    if options:
        query_text += "\n" + "\n".join(options)

    # BM25 search
    bm25_top = max(config.RERANK_TOP_K, top_k_final * 3)
    bm25_results = bm25_store.search(query_text, top_k=bm25_top)

    if not bm25_results:
        return []

    # Filter dividers, prefer content pages
    content_pages = [r for r in bm25_results if not r.is_divider]
    divider_pages = [r for r in bm25_results if r.is_divider]
    candidates = content_pages + divider_pages

    # Convert to SearchResult objects
    candidate_objs = [_bm25_result_to_obj(r) for r in candidates[:config.RERANK_TOP_K]]

    # Optional LLM rerank
    if config.RERANK_ENABLED and len(candidate_objs) > top_k_final:
        from backend.retrieval import reranker
        return reranker.rerank(question, candidate_objs, top_k=top_k_final)

    return candidate_objs[:top_k_final]


hybrid_search = query_for_retrieval
