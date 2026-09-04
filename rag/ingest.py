"""Seeds ChromaDB from data/corpus. Does NOT auto-ingest data/corpus/poisoned/
-- those fixtures are loaded explicitly by attacks/01/attack_retrieval_poisoning.py
so the foundation smoke test stays clean/benign by default.
"""
from pathlib import Path

from rag.chroma_store import get_collection

CORPUS_DIR = Path("/data/corpus")


def ingest_benign_corpus() -> int:
    collection = get_collection()
    docs, ids, metadatas = [], [], []
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        docs.append(path.read_text())
        ids.append(path.stem)
        metadatas.append({"source": path.name, "trust": "seed"})
    if docs:
        collection.upsert(documents=docs, ids=ids, metadatas=metadatas)
    return len(docs)


def ingest_poisoned_doc(doc_path: Path) -> str:
    """Explicit, separate ingestion path for module-1 attack fixtures --
    never called by the benign smoke test."""
    collection = get_collection()
    doc_id = f"poisoned-{doc_path.stem}"
    collection.upsert(
        documents=[doc_path.read_text()],
        ids=[doc_id],
        metadatas=[{"source": doc_path.name, "trust": "untrusted"}],
    )
    return doc_id


if __name__ == "__main__":
    count = ingest_benign_corpus()
    print(f"Ingested {count} benign documents.")
