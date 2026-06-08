"""LLM reranker: selects top-k relevant pages from BM25 candidates."""
from __future__ import annotations

import asyncio
import logging
from typing import List

import httpx

from backend import config

logger = logging.getLogger(__name__)


async def _rerank_batch(question: str, candidates: list, top_k: int) -> list[int]:
    """Ask LLM to pick top-k indices. Returns list of selected indices."""
    items = []
    for i, c in enumerate(candidates):
        text = c.full_text[:200] if hasattr(c, 'full_text') else str(c)[:200]
        items.append(f"[{i}] {text}")

    prompt = f"""选出与问题最相关的{top_k}个页面，返回JSON数组如[0,3,5]。只返回JSON数组。

问题：{question}

页面：
{chr(10).join(items)}

JSON数组："""

    headers = {"Content-Type": "application/json"}
    if config.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {config.LLM_API_KEY}"

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=config.LLM_TIMEOUT) as client:
                resp = await client.post(
                    config.LLM_API_URL,
                    json={
                        "model": config.LLM_MODEL,
                        "max_tokens": 80,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                raw = data["choices"][0]["message"]["content"].strip()
                import json
                start = raw.find("[")
                end = raw.rfind("]") + 1
                if start >= 0 and end > start:
                    indices = json.loads(raw[start:end])
                    if isinstance(indices, list):
                        return [i for i in indices if isinstance(i, int) and 0 <= i < len(candidates)]
        except Exception as e:
            if attempt < 1:
                await asyncio.sleep(0.5)
            else:
                logger.warning("Reranker LLM failed: %s", e)

    # Fallback: return top indices by original order
    return list(range(min(top_k, len(candidates))))


def rerank(question: str, candidates: list, top_k: int = 5) -> list:
    """Sync wrapper — picks top_k pages via LLM."""
    if not candidates:
        return []
    if len(candidates) <= top_k:
        return candidates

    try:
        selected = asyncio.run(_rerank_batch(question, candidates, top_k))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, _rerank_batch(question, candidates, top_k))
                selected = future.result()
        else:
            selected = asyncio.run(_rerank_batch(question, candidates, top_k))

    result = []
    for idx in selected:
        if 0 <= idx < len(candidates):
            candidates[idx].score = 1.0 - idx * 0.05  # descending confidence
            result.append(candidates[idx])
    return result[:top_k]
