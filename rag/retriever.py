"""Top-k retrieval.

Vulnerable mode: NO provenance/trust check -- retrieved text flows straight
into the planner's prompt. Secure mode: drops chunks marked trust=untrusted
(poison fixtures used by Module 1).
"""
from defenses.config import is_secure
from rag.chroma_store import get_collection


def retrieve(query: str, top_k: int = 3) -> list[str]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    n = min(top_k * 3 if is_secure() else top_k, collection.count())
    results = collection.query(
        query_texts=[query],
        n_results=n,
        include=["documents", "metadatas"],
    )
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0] or [{}] * len(documents)

    out: list[str] = []
    for doc, meta in zip(documents, metadatas):
        meta = meta or {}
        if is_secure() and meta.get("trust") == "untrusted":
            continue
        out.append(doc)
        if len(out) >= top_k:
            break
    return out
