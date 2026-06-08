"""Embedder stub — vector search removed; BM25+LLM rerank is used instead."""
from typing import List


class Embedder:
    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Vector embedding not used; use BM25 retrieval.")


_embedder = Embedder()
embedder = _embedder


def get_embedder() -> Embedder:
    return _embedder
