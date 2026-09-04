"""Module 2 defense: retrieval-time poison detection.

Module 1's RAG filter only drops chunks whose *metadata* says trust=untrusted.
That fails against two deeper attacks this module teaches:

1. **False provenance** — the attacker labels a poisoned chunk trust=seed, so the
   metadata filter waves it through.
2. **Embedding-space crowding** — the attacker floods the corpus with many
   near-duplicate poison chunks so they dominate top-k for a target query.

The detector below looks at the *content* (not just the label): it flags chunks
that carry instruction-shaped text aimed at the assistant, and it collapses
near-duplicate crowding so a flood counts once. Returned reasons drive the
lesson's DEFENSE lines. Pure-Python and deterministic — no model needed.
"""
from __future__ import annotations

import re

# Phrases that indicate a document is trying to *instruct* the agent rather than
# inform it. Retrieved data should never contain imperatives aimed at the model.
INSTRUCTION_MARKERS = (
    "system note", "assistant:", "ignore previous", "ignore all previous",
    "you must", "your task is", "export all", "send them to", "email them",
    "disregard", "override", "as an ai", "do the following",
)
EXFIL_MARKERS = ("1=1", "select *", "customers", "@external", "@evil", "@attacker")
EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)


def _instruction_score(text: str) -> tuple[int, list[str]]:
    low = text.lower()
    hits = [m for m in INSTRUCTION_MARKERS if m in low]
    hits += [m for m in EXFIL_MARKERS if m in low]
    if EMAIL_RE.search(text):
        hits.append("embedded-email-address")
    return len(hits), hits


def _shingles(text: str, k: int = 4) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(toks[i:i + k]) for i in range(max(0, len(toks) - k + 1))}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def classify_chunks(chunks: list[str], *, dup_threshold: float = 0.6) -> list[dict]:
    """Return one verdict per chunk: quarantine + reason(s).

    A chunk is quarantined if it carries instruction-shaped content, OR if it is
    a near-duplicate of an earlier chunk (crowding). The first member of a
    near-duplicate cluster is kept if it is otherwise clean, so legitimate
    repetition is tolerated but a flood is collapsed.
    """
    verdicts: list[dict] = []
    kept_shingles: list[set[str]] = []
    for text in chunks:
        reasons: list[str] = []
        score, hits = _instruction_score(text)
        if score >= 1:
            reasons.append(f"instruction-shaped content ({', '.join(hits[:3])})")
        sh = _shingles(text)
        if any(_jaccard(sh, prev) >= dup_threshold for prev in kept_shingles):
            reasons.append("near-duplicate crowding")
        quarantine = bool(reasons)
        if not quarantine:
            kept_shingles.append(sh)
        verdicts.append({"quarantine": quarantine, "reasons": reasons, "preview": text[:120]})
    return verdicts


def filter_poison(chunks: list[str]) -> tuple[list[str], list[dict]]:
    """Return (clean_chunks, quarantined_verdicts)."""
    verdicts = classify_chunks(chunks)
    clean = [c for c, v in zip(chunks, verdicts) if not v["quarantine"]]
    quarantined = [v for v in verdicts if v["quarantine"]]
    return clean, quarantined
