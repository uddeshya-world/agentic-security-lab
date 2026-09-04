"""LLM09 defense: groundedness / citation enforcement.

**Scope, stated honestly:** this is *not* a hallucination detector. Detecting
whether a statement is true in general is not something a deterministic lab check
can do, and pretending otherwise would be theater.

What this *is* — and what production RAG systems actually deploy — is a
**groundedness check**: every factual claim in an answer must be supported by the
retrieved context the answer was built from. An unsupported claim is blocked or
must carry a citation. That catches the two failure modes that matter here:

1. the model asserts a policy that exists nowhere in the corpus (fabrication), and
2. the model confidently repeats a *poisoned* corpus claim (misinformation as a
   downstream consequence of Module 2/6 poisoning) — where citation makes the bad
   source visible instead of laundering it as the agent's own voice.

Support is measured by content-word overlap between a claim and each context
chunk, which is deterministic and dependency-free.
"""
from __future__ import annotations

import re

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "to", "of",
    "and", "or", "in", "on", "for", "with", "as", "at", "by", "from", "that", "this",
    "these", "those", "it", "its", "you", "your", "we", "our", "us", "will", "can",
    "may", "do", "does", "did", "have", "has", "had", "not", "but", "if", "then",
    "there", "their", "they", "he", "she", "i", "up", "out", "so", "than", "also",
}


def _claims(answer: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", answer or "")
    return [p.strip() for p in parts if len(p.strip()) > 12]


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if w not in STOPWORDS and len(w) > 2}


def support_score(claim: str, chunk: str) -> float:
    """Fraction of the claim's content words present in the chunk."""
    cw = _content_words(claim)
    if not cw:
        return 1.0
    return len(cw & _content_words(chunk)) / len(cw)


def verify(answer: str, context_chunks: list[str], *, threshold: float = 0.6) -> dict:
    """Return per-claim grounding verdicts plus a citation for each supported claim."""
    results = []
    for claim in _claims(answer):
        best_idx, best = -1, 0.0
        for i, chunk in enumerate(context_chunks or []):
            s = support_score(claim, chunk)
            if s > best:
                best_idx, best = i, s
        grounded = best >= threshold
        results.append({
            "claim": claim[:120],
            "grounded": grounded,
            "support": round(best, 2),
            "citation": f"[source {best_idx + 1}]" if grounded else None,
        })
    unsupported = [r for r in results if not r["grounded"]]
    return {
        "claims": results,
        "unsupported": unsupported,
        "all_grounded": not unsupported,
    }


def enforce(answer: str, context_chunks: list[str], *, threshold: float = 0.6) -> tuple[str, dict]:
    """Return (safe_answer, verdict). Unsupported claims are withheld, not shipped."""
    verdict = verify(answer, context_chunks, threshold=threshold)
    if verdict["all_grounded"]:
        cited = " ".join(
            f"{r['claim']} {r['citation']}" for r in verdict["claims"]
        )
        return (cited or answer), verdict
    kept = [f"{r['claim']} {r['citation']}" for r in verdict["claims"] if r["grounded"]]
    note = ("[withheld: "
            f"{len(verdict['unsupported'])} claim(s) not supported by retrieved sources]")
    return (" ".join(kept + [note]).strip()), verdict
