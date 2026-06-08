"""Shared async/sync LLM API client for all QA modules."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Lazy import config to avoid circular imports at module level
def _get_config():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from backend import config
    return config


def _build_payload(prompt: str, max_tokens: int) -> dict:
    cfg = _get_config()
    return {
        "model": cfg.LLM_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }


def _build_headers() -> dict:
    cfg = _get_config()
    headers = {"Content-Type": "application/json"}
    if cfg.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {cfg.LLM_API_KEY}"
    return headers


async def acall_llm(prompt: str, max_tokens: int = 200) -> str:
    """Async LLM call with 2 retries."""
    cfg = _get_config()
    payload = _build_payload(prompt, max_tokens)
    headers = _build_headers()
    last_exc: Optional[Exception] = None

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=cfg.LLM_TIMEOUT) as client:
                resp = await client.post(cfg.LLM_API_URL, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_exc = e
            if attempt < 2:
                await asyncio.sleep(1.0 * (attempt + 1))
            logger.warning("LLM call attempt %d failed: %s", attempt + 1, e)

    logger.error("LLM call failed after 3 attempts: %s", last_exc)
    return ""


def call_llm(prompt: str, max_tokens: int = 200) -> str:
    """Sync wrapper around acall_llm."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In async context (e.g. benchmark runner), use a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, acall_llm(prompt, max_tokens))
                return future.result()
        else:
            return loop.run_until_complete(acall_llm(prompt, max_tokens))
    except RuntimeError:
        return asyncio.run(acall_llm(prompt, max_tokens))
