"""These tests import rag/ directly (in-process ChromaDB), so they must run
INSIDE the agent container, not from the host:
    docker compose exec agent pytest tests/test_rag.py -v
"""
from rag.ingest import ingest_benign_corpus
from rag.retriever import retrieve


def test_ingest_and_retrieve():
    count = ingest_benign_corpus()
    assert count >= 3
    results = retrieve("What is your return policy?")
    assert any("return" in r.lower() or "refund" in r.lower() for r in results)
