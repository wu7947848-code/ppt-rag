import pickle
import logging
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

import jieba
import numpy as np
from rank_bm25 import BM25Okapi

from backend import config

logger = logging.getLogger(__name__)

_BM25_PATH = config.INDEX_DIR / "bm25.pkl"

# Regex for English words, numbers with units, Chinese characters
_RE_EN_WORD = re.compile(r'[a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*')
_RE_NUMBER_UNIT = re.compile(r'\d+[\.\d]*\s*[%°℃]?')
_RE_HAS_CHINESE = re.compile(r'[一-鿿]')

# Domain-specific terms to preserve (prevent jieba from splitting)
_KEEP_TERMS = {
    'FusionDirector', 'FusionXpark', 'FusionServer', 'HBM3e', 'HBM3E', 'HBM',
    'CoWoS', 'Chiplet', 'eVTOL', 'UAM', 'HPC', 'iBMC', 'GPU', 'CPU', 'SSD',
    'NVMe', 'LPDDR5x', 'DDR5', 'Wi-Fi', 'TMDs', 'SiP', 'Bump', 'Hybrid Bonding',
    'Redfish', 'LDAP', 'Kerberos', 'CVD', 'Smart Provisioning', 'GB10',
    '2288 V7', '2258H V8', '1158H V7', 'BGE', 'MRR', 'NDCG',
}


def _tokenize(text: str) -> List[str]:
    """Tokenize mixed Chinese-English text preserving technical terms."""
    if not text:
        return []

    tokens = []

    # 1. Extract domain-specific terms first (case-insensitive for English)
    remaining = text
    for term in sorted(_KEEP_TERMS, key=len, reverse=True):
        idx = remaining.lower().find(term.lower())
        if idx >= 0:
            # Tokenize the part before the term
            if idx > 0:
                tokens.extend(_tokenize_plain(remaining[:idx]))
            tokens.append(term)
            remaining = remaining[idx + len(term):]

    if remaining:
        tokens.extend(_tokenize_plain(remaining))

    # Remove noise tokens
    noise = set(' .,;:!?()[]{}\"\'\\/-_=+<>|&^%$#@!~`')
    tokens = [t for t in tokens if t.strip() and t not in noise and len(t) > 0]
    return tokens


def _tokenize_plain(text: str) -> List[str]:
    """Tokenize general mixed text."""
    tokens = []

    # Split on whitespace first
    parts = text.split()
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check if contains Chinese
        if _RE_HAS_CHINESE.search(part):
            # Extract leading English/number prefix
            en_prefix = ''
            m = re.match(r'^([a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*)', part)
            if m:
                en_prefix = m.group(1)
                part = part[len(en_prefix):]
                if en_prefix:
                    tokens.append(en_prefix.lower())

            # Extract trailing English/number suffix
            en_suffix = ''
            m = re.search(r'([a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*)$', part)
            if m:
                en_suffix = m.group(1)
                part = part[:-len(en_suffix)]
                if en_suffix:
                    tokens.append(en_suffix.lower())

            # Jieba the Chinese part
            if part:
                tokens.extend([t for t in jieba.lcut(part, cut_all=False) if t.strip()])
        else:
            # Pure English/number part
            for word in _RE_EN_WORD.findall(part):
                tokens.append(word.lower())

    return [t for t in tokens if t.strip()]



@dataclass
class SearchResult:
    doc_id: str
    filename: str
    page_num: int
    title: str
    full_text: str
    score: float
    is_divider: bool = False


class BM25Store:
    def __init__(self):
        self._bm25: Optional[BM25Okapi] = None
        self._pages: List[dict] = []
        self._load()

    def _load(self):
        if _BM25_PATH.exists():
            try:
                with open(_BM25_PATH, "rb") as f:
                    data = pickle.load(f)
                self._bm25 = data["bm25"]
                self._pages = data["pages"]
                logger.info("BM25 loaded: %d pages", len(self._pages))
            except Exception as e:
                logger.warning("Failed to load BM25: %s", e)

    def build(self):
        """Rebuild BM25 index from all indexed docs in PAGES_DIR."""
        from backend.index import catalog
        docs = catalog.list_all(status_filter="indexed")

        pages = []
        corpus = []

        for doc in docs:
            doc_id = doc["doc_id"]
            jsonl_path = config.PAGES_DIR / f"{doc_id}.jsonl"
            if not jsonl_path.exists():
                continue
            try:
                import json
                with open(jsonl_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        page_data = json.loads(line)
                        pages.append(page_data)
                        corpus.append(_tokenize(page_data.get("full_text", "")))
            except Exception as e:
                logger.warning("Failed to read %s: %s", jsonl_path, e)

        if not corpus:
            logger.info("No pages to index for BM25")
            self._bm25 = None
            self._pages = []
            return

        try:
            self._bm25 = BM25Okapi(corpus, k1=1.5, b=0.75)
        except (ValueError, ZeroDivisionError) as e:
            logger.warning("BM25Okapi init failed (corpus too small?): %s", e)
            self._bm25 = None
            self._pages = []
            return

        self._pages = pages
        _BM25_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_BM25_PATH, "wb") as f:
            pickle.dump({"bm25": self._bm25, "pages": self._pages}, f)
        logger.info("BM25 rebuilt: %d pages", len(pages))

    def rebuild(self):
        self.build()

    def search(self, query: str, top_k: int = 50) -> List[SearchResult]:
        if self._bm25 is None or not self._pages:
            return []

        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            page = self._pages[idx]
            results.append(SearchResult(
                doc_id=page.get("doc_id", ""),
                filename=page.get("filename", ""),
                page_num=page.get("page_num", 0),
                title=page.get("title", ""),
                full_text=page.get("full_text", ""),
                score=score,
                is_divider=page.get("is_divider", False),
            ))
        return results


_store: Optional[BM25Store] = None


def _get_store() -> BM25Store:
    global _store
    if _store is None:
        _store = BM25Store()
    return _store


def rebuild():
    _get_store().build()


def search(query: str, top_k: int = 50) -> List[SearchResult]:
    return _get_store().search(query, top_k)


bm25_store = _get_store()
