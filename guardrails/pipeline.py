"""Module 5: a real (lightweight) guardrail pipeline + measured effectiveness.

The ``nemo_seam.py`` / ``llmguard_seam.py`` files are no-op passthroughs. This
module is a working, measurable stand-in for a production guardrail layer:
heuristic input/output scanners (the same shape LLM Guard / NeMo rules take),
run over a labeled probe set so we can report the numbers that actually matter —
catch rate, false-positive rate, and latency — instead of a toy pass/fail.

Everything is deterministic and dependency-free, so the dashboard reproduces.
"""
from __future__ import annotations

import re
import time

# --- input scanners: catch prompt-injection / jailbreak shapes ---
_INJECTION_RE = re.compile(
    r"(ignore (all )?previous|disregard (the )?(above|instructions)|system note|"
    r"you are now|developer mode|exfiltrate|filter\s*=\s*1=1|send .* to .*@)", re.I,
)
# --- output scanners: catch data egress / secret leakage ---
_PII_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
_SECRET_RE = re.compile(r"(sk-[a-z0-9]{8,}|AKIA[0-9A-Z]{12,}|password\s*[:=])", re.I)
# Data guards (C21): structured PII beyond "looks like an email".
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PAN_RE = re.compile(r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14})\b")

# Teaching labels — not a real taxonomy engine.
CLASSIFICATION = ("public", "internal", "confidential", "restricted")


def find_sensitive(text: str) -> list[dict]:
    """Return labelled hits for DLP labs. Deterministic, no ML."""
    t = text or ""
    hits: list[dict] = []
    for m in _SSN_RE.finditer(t):
        hits.append({"type": "ssn", "value": m.group(0), "class": "restricted"})
    for m in _PAN_RE.finditer(t):
        hits.append({"type": "pan", "value": m.group(0), "class": "restricted"})
    for m in _SECRET_RE.finditer(t):
        hits.append({"type": "secret", "value": m.group(0), "class": "restricted"})
    for m in _PII_RE.finditer(t):
        hits.append({"type": "email", "value": m.group(0), "class": "confidential"})
    return hits


def mask_sensitive(text: str) -> str:
    t = text or ""
    t = _SSN_RE.sub("[SSN]", t)
    t = _PAN_RE.sub("[PAN]", t)
    t = _SECRET_RE.sub("[SECRET]", t)
    t = _PII_RE.sub("[EMAIL]", t)
    return t


def scan_data(text: str, *, channel: str) -> dict:
    """Four-channel data guard: input | context | output | tool."""
    hits = find_sensitive(text)
    restricted = [h for h in hits if h["class"] == "restricted"]
    # Restricted → block the channel. Confidential (email) → mask, still a hit.
    action = "block" if restricted else ("mask" if hits else "allow")
    return {
        "blocked": action in ("block", "mask") and bool(restricted or channel in ("output", "tool") and hits),
        "action": action,
        "channel": channel,
        "hits": [{"type": h["type"], "class": h["class"]} for h in hits],
        "masked": mask_sensitive(text),
        "scanner": "data-guard",
    }


def scan_input(text: str) -> dict:
    hit = bool(_INJECTION_RE.search(text or ""))
    return {"blocked": hit, "scanner": "prompt-injection", "channel": "input"}


def scan_output(text: str, *, allow_domain: str = "@example.test") -> dict:
    emails = [e for e in _PII_RE.findall(text or "") if not e.endswith(allow_domain)]
    secret = bool(_SECRET_RE.search(text or ""))
    hit = bool(emails) or secret
    reason = "secret-leak" if secret else ("pii-egress" if emails else "clean")
    return {"blocked": hit, "scanner": reason, "channel": "output"}


def evaluate(text: str, *, channel: str = "input") -> dict:
    start = time.perf_counter()
    verdict = scan_input(text) if channel == "input" else scan_output(text)
    verdict["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
    return verdict


def run_benchmark(probes: list[dict]) -> dict:
    """probes: [{text, channel, malicious: bool}]. Returns effectiveness metrics."""
    tp = fp = tn = fn = 0
    latencies: list[float] = []
    for p in probes:
        v = evaluate(p["text"], channel=p.get("channel", "input"))
        latencies.append(v["latency_ms"])
        if p["malicious"] and v["blocked"]:
            tp += 1
        elif p["malicious"] and not v["blocked"]:
            fn += 1
        elif not p["malicious"] and v["blocked"]:
            fp += 1
        else:
            tn += 1
    mal = tp + fn
    benign = fp + tn
    latencies.sort()

    def pct(idx):
        return latencies[min(len(latencies) - 1, int(idx * len(latencies)))] if latencies else 0.0

    return {
        "total": len(probes),
        "catch_rate": round(tp / mal, 3) if mal else 0.0,
        "false_positive_rate": round(fp / benign, 3) if benign else 0.0,
        "true_positives": tp, "false_negatives": fn,
        "false_positives": fp, "true_negatives": tn,
        "p50_latency_ms": pct(0.50), "p95_latency_ms": pct(0.95),
    }
