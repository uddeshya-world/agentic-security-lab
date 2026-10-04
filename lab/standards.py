"""Registry of the external standards this lab cites beside the OWASP LLM / ASI lists.

Two OWASP projects, both Incubator, both CC BY-SA 4.0:

* **AISVS v1.0** (AI Security Verification Standard, locked). What to *verify*.
  Cite as ``AISVS v1.0 C9.2.1 (L1)``. Lab controls are also numbered C1–C21, so an
  AISVS id is always written with the ``AISVS v1.0`` prefix outside this file and
  ``lab/curriculum.py`` (``tests/test_standards_registry.py`` enforces it).
* **Agentic Skills Top 10 v1.0-2026** (AST01–AST10). A risk list for agent skills.

Licence hygiene: this repo is Apache-2.0, so it stores ids, chapter names, levels and
**our own one-line paraphrase** plus a link. It never stores requirement text. Read the
requirement itself at the URL before relying on a paraphrase.
"""
from __future__ import annotations

AISVS_VERSION = "v1.0"
AISVS_URL = "https://github.com/OWASP/AISVS/tree/main/1.0/en"
AST_VERSION = "v1.0-2026"
AST_URL = "https://github.com/OWASP/www-project-agentic-skills-top-10"

# Chapter names as each chapter file's H1 states them. ``count`` = requirement ids in
# that chapter, counted from the published v1.0 files on 2026-10-04 (191 in total).
AISVS_CHAPTERS: dict[str, dict] = {
    "C1": {"name": "Training Data Integrity & Traceability", "count": 13},
    "C2": {"name": "Input Validation", "count": 12},
    "C3": {"name": "Model Lifecycle Management & Change Control", "count": 15},
    "C4": {"name": "Infrastructure, Configuration & Deployment Security", "count": 14},
    "C5": {"name": "Access Control & Identity for AI Components & Users", "count": 11},
    "C6": {"name": "Supply Chain Security for Models", "count": 7},
    "C7": {"name": "Model Behavior, Output Control & Safety Assurance", "count": 13},
    "C8": {"name": "Memory, Embeddings & Vector Database Security", "count": 11},
    "C9": {"name": "Orchestration & Agentic Security", "count": 34},
    "C10": {"name": "Model Context Protocol (MCP) Security", "count": 23},
    "C11": {"name": "Adversarial Robustness", "count": 17},
    "C12": {"name": "Monitoring, Logging & Anomaly Detection", "count": 21},
}

# Chapters this lab does not exercise, and why. Listed so coverage is not self-selected.
AISVS_OUT_OF_SCOPE: dict[str, str] = {
    "C1": "Training-data provenance is a model-builder concern; this lab runs a stock local model.",
    "C3": "Model lifecycle and change control sit with whoever trains and ships the model.",
    "C4": "Infrastructure hardening is platform work; the lab is a deliberately weak local stack.",
    "C11": "Adversarial robustness is a property of the model itself; the lab tests controls outside the model.",
}

# Requirements this lab cites. Paraphrases are ours (see module docstring).
AISVS_REQUIREMENTS: dict[str, dict] = {
    "C2.1.3": {"level": 1, "summary": "Treat anything that can steer the model as untrusted; screen it and block what is flagged."},
    "C5.2.7": {"level": 3, "summary": "Data classification labels follow the data into downstream stores and outputs."},
    "C6.2.2": {"level": 2, "summary": "The AI bill of materials is signed before deployment."},
    "C7.1.1": {"level": 1, "summary": "Model output is checked against a schema and rejected when it does not fit."},
    "C7.3.2": {"level": 2, "summary": "Output filtering stops responses that reveal the system prompt or backend data."},
    "C7.3.3": {"level": 2, "summary": "Model output cannot by itself cause outbound requests."},
    "C7.4.1": {"level": 1, "summary": "Answers built from retrieval cite the documents they came from."},
    "C7.4.2": {"level": 1, "summary": "Citations come from retrieval metadata, not from the model's own text."},
    "C7.4.3": {"level": 2, "summary": "Each claim in a retrieval answer traces back to a retrieved chunk."},
    "C8.2.1": {"level": 1, "summary": "Sensitive fields are found and masked or dropped before embedding."},
    "C8.2.3": {"level": 2, "summary": "Agent and tool output reaches trusted memory only after its source is validated."},
    "C8.2.4": {"level": 3, "summary": "Content built to game retrieval is caught before it is vectorised."},
    "C9.1.1": {"level": 1, "summary": "Each tool runs under quotas and timeouts."},
    "C9.1.2": {"level": 1, "summary": "Each run has budgets (depth, tokens, spend) the runtime enforces."},
    "C9.2.1": {"level": 1, "summary": "High-impact or irreversible actions wait for a verified human approval."},
    "C9.2.2": {"level": 2, "summary": "Approval prompts show the full, untruncated action parameters."},
    "C9.2.10": {"level": 3, "summary": "Approval for a multi-step or multi-agent chain uses the most severe action anywhere in it."},
    "C9.3.3": {"level": 2, "summary": "Tool manifests state the privileges and limits the tool needs."},
    "C9.3.4": {"level": 2, "summary": "The runtime enforces what the tool manifest declares."},
    "C9.3.5": {"level": 2, "summary": "Parts that handle untrusted data are kept away from tool calling."},
    "C9.3.7": {"level": 2, "summary": "Resources the model names are checked against an allow-list or registry before use."},
    "C9.4.1": {"level": 2, "summary": "Every agent instance has its own cryptographic identity."},
    "C9.4.2": {"level": 2, "summary": "Each step an agent takes is cryptographically bound for non-repudiation."},
    "C9.5.1": {"level": 2, "summary": "A runtime policy limits which tools an agent may call and with which parameter values."},
    "C9.5.2": {"level": 2, "summary": "Acting for a user carries a scoped, integrity-protected token checked at every hop."},
    "C9.5.3": {"level": 2, "summary": "Access decisions are made by application logic or a policy engine, never by the model."},
    "C9.5.5": {"level": 2, "summary": "Delegation between agents is limited by an explicit policy."},
    "C9.6.2": {"level": 2, "summary": "An approval that times out blocks the action."},
    "C10.1.2": {"level": 2, "summary": "Only allow-listed MCP servers may connect."},
    "C10.4.3": {"level": 1, "summary": "MCP servers reject unknown or oversized call parameters."},
    "C10.4.8": {"level": 3, "summary": "Tool definitions are snapshotted; any change needs re-approval before the tool runs."},
    "C11.1.3": {"level": 1, "summary": "Models are evaluated against known adversarial techniques."},
    "C12.1.2": {"level": 2, "summary": "Safety and policy decisions are logged in enough detail to audit."},
    "C12.2.1": {"level": 1, "summary": "Known jailbreak and injection patterns are detected and alerted on."},
    "C12.4.2": {"level": 2, "summary": "Audit logs record approver, time, parameters and outcome of security actions."},
    "C12.5.4": {"level": 2, "summary": "Ingested documents are tagged with source, writer and time when written."},
}

AST: dict[str, str] = {
    "AST01": "Malicious Skills",
    "AST02": "Supply Chain Compromise",
    "AST03": "Over-Privileged Skills",
    "AST04": "Insecure Metadata",
    "AST05": "Untrusted External Instructions",
    "AST06": "Weak Isolation",
    "AST07": "Update Drift",
    "AST08": "Poor Scanning",
    "AST09": "No Governance",
    "AST10": "Cross-Platform Reuse",
}

# AST entries the lab touches without a scenario that declares them. Said plainly.
AST_PARTIAL: dict[str, str] = {
    "AST09": "Reviewer track and Reviewer mode ask for a skill inventory and approval; no scenario exercises it.",
}

STRENGTHS = ("demonstrates", "partial")


def aisvs_label(rid: str) -> str:
    """The one way an AISVS id is shown to people: version-prefixed, with its level."""
    return f"AISVS {AISVS_VERSION} {rid} (L{AISVS_REQUIREMENTS[rid]['level']})"


def aisvs_chapter(rid: str) -> str:
    return rid.split(".")[0]


def control_mappings(controls: list[dict]) -> list[dict]:
    """Flatten ``CONTROLS[*].aisvs`` into rows: control, requirement, strength, proof."""
    rows = []
    for c in controls:
        for m in c.get("aisvs") or []:
            rows.append({"control": c["id"], "control_name": c["name"], **m})
    return rows


def scenario_aisvs(scenario_id: str, scenario_controls: list[str], controls: list[dict]) -> list[dict]:
    """What a scenario lets you verify, derived (never authored) so it cannot overclaim.

    *demonstrates* only where a control's ``proven_by`` points at a graded check in this
    scenario; otherwise every requirement its controls cite shows as *partial*.
    """
    best: dict[str, str] = {}
    for c in controls:
        if c["id"] not in scenario_controls:
            continue
        for m in c.get("aisvs") or []:
            proven_here = any(p.split("/")[0] == scenario_id for p in m.get("proven_by") or [])
            strength = "demonstrates" if (m["strength"] == "demonstrates" and proven_here) else "partial"
            if best.get(m["id"]) != "demonstrates":
                best[m["id"]] = strength
    order = {"demonstrates": 0, "partial": 1}
    return [
        {"id": rid, "strength": s, "label": aisvs_label(rid)}
        for rid, s in sorted(best.items(), key=lambda kv: (order[kv[1]], kv[0]))
    ]
