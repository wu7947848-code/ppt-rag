"""Query rewriting: LLM extracts search keywords from user questions."""
from __future__ import annotations

import asyncio
import logging
from typing import List

import httpx

from backend import config

logger = logging.getLogger(__name__)


async def _extract_keywords_async(question: str, options: list = None) -> str:
    """Let LLM extract dense keywords suitable for BM25 matching."""
    options_text = ""
    if options:
        options_text = "\n选项：\n" + "\n".join(f"{chr(65 + i)}. {opt}" for i, opt in enumerate(options))

    prompt = f"""从以下问题中提取用于文档搜索的关键词列表。要求：
- 包含专有名词、数字、缩写等精确匹配词
- 同时包含同义词、相关概念（如"诊断准确率"可扩展为"诊断 准确率 故障检测 精度"）
- 用空格分隔，15个词以内

问题：{question}{options_text}
关键词："""

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
                keywords = data["choices"][0]["message"]["content"].strip()
                return keywords
        except Exception as e:
            if attempt < 1:
                await asyncio.sleep(0.5)
            else:
                logger.warning("Keyword extraction failed: %s", e)

    return question  # Fallback: use original question


def expand_query(question: str, options: list = None) -> str:
    """Sync wrapper. Returns original question + extracted keywords."""
    try:
        keywords = asyncio.run(_extract_keywords_async(question, options))
    except RuntimeError:
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, _extract_keywords_async(question, options))
                keywords = future.result()
        except Exception:
            keywords = question
    except Exception:
        keywords = question

    # Combine: original question + keywords for BM25
    if keywords and keywords != question:
        return f"{question}\n{keywords}"
    return question
