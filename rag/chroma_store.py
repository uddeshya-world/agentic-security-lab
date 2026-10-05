"""Chroma persistent store with an offline embedding function.

Default Chroma ONNX MiniLM download often times out in Docker/lab networks.
We use a deterministic bag-of-words hash embedding so RAG demos work fully
offline. Quality is lower than MiniLM, but keyword overlap (e.g. shipping /
poison fixtures) is enough for Module 1 teaching demos.
"""
from __future__ import annotations

import hashlib
import math
from typing import Sequence

import chromadb
import chromadb.config
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

CHROMA_PATH = "/data/chroma"
# New name so an empty/default-EF collection from a prior run cannot conflict.
COLLECTION_NAME = "lab_corpus_hash_v1"
EMBED_DIM = 384


class HashEmbeddingFunction(EmbeddingFunction[Documents]):
    """Offline, deterministic embeddings for lab use only."""

    def __init__(self, dim: int = EMBED_DIM):
        self.dim = dim

    def __call__(self, input: Documents) -> Embeddings:
        out: list[list[float]] = []
        for text in input:
            vec = [0.0] * self.dim
            tokens = text.lower().replace("\n", " ").split()
            if not tokens:
                tokens = ["_empty_"]
            for token in tokens:
                h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
                vec[h % self.dim] += 1.0
                # Bigrams for slightly better local similarity
                # (handled by consecutive tokens via pair hash)
            for a, b in zip(tokens, tokens[1:]):
                h = int(hashlib.md5(f"{a}_{b}".encode("utf-8")).hexdigest(), 16)
                vec[h % self.dim] += 0.5
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            out.append([x / norm for x in vec])
        return out


_client = None
_collection = None
_ef = HashEmbeddingFunction()


def get_collection():
    global _client, _collection
    if _collection is None:
        # Telemetry off: the lab promises nothing leaves the machine.
        _client = chromadb.PersistentClient(
            path=CHROMA_PATH, settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=_ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection
