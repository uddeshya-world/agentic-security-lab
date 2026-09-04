"""AI security curriculum: OWASP mapping, controls taught, remediations.

This is the "blue team / how to stop it" layer students need after red-team demos.
"""
from __future__ import annotations

# OWASP LLM Top 10 (2025 naming as used in SECURITY_NOTES) + Agentic ASI themes.
OWASP_LLM = {
    "LLM01": {
        "name": "Prompt Injection (direct & indirect)",
        "covered": True,
        "where_in_lab": ["indirect_pi", "a2", "a4"],
        "student_learns": "Untrusted text (RAG/docs) can become instructions to the agent.",
    },
    "LLM02": {
        "name": "Sensitive Information Disclosure",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "a3", "a4"],
        "student_learns": "Tools can dump PII (customers) and leak it via answers or email.",
    },
    "LLM03": {
        "name": "Supply Chain",
        "covered": True,
        "where_in_lab": ["m7"],
        "student_learns": "Rogue/tampered tools & MCP servers; signed manifests + attestation (Module 7).",
    },
    "LLM04": {
        "name": "Data and Model Poisoning",
        "covered": True,
        "where_in_lab": ["indirect_pi", "a2"],
        "student_learns": "Poisoned corpus documents change agent behavior after retrieval.",
    },
    "LLM05": {
        "name": "Improper Output Handling",
        "covered": True,
        "where_in_lab": ["m5"],
        "student_learns": "Output scanner blocks PII egress and secret leakage (Module 5).",
    },
    "LLM06": {
        "name": "Excessive Agency",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "path_read", "a1", "a3", "a4"],
        "student_learns": "Agent can call high-impact tools without enough authorization.",
    },
    "LLM07": {
        "name": "System Prompt Leakage",
        "covered": True,
        "where_in_lab": ["m9"],
        "student_learns": "Leaked prompt = recon (tool names, arg shapes, dump-all example); detect on output, keep secrets out of the prompt.",
    },
    "LLM08": {
        "name": "Vector and Embedding Weaknesses",
        "covered": True,
        "where_in_lab": ["a2", "indirect_pi"],
        "student_learns": "Retrieval can surface attacker-chosen chunks into context.",
    },
    "LLM09": {
        "name": "Misinformation",
        "covered": True,
        "where_in_lab": ["m10"],
        "student_learns": (
            "Groundedness/citation enforcement: unsupported claims are withheld. "
            "Scope: verifies SUPPORT BY SOURCES, not truth in general."
        ),
    },
    "LLM10": {
        "name": "Unbounded Consumption",
        "covered": True,
        "where_in_lab": ["m11"],
        "student_learns": "Denial of wallet: step cap + cost budget + loop detection + rate limit.",
    },
}

# Agentic threat themes (OWASP Agentic Security Initiative / agentic AI threat
# taxonomy). NOTE ON HONESTY: the ASI0X ids below are this lab's own stable
# handles, mapped to the published agentic threat themes — they are not a claim to
# reproduce OWASP's official numbering verbatim. Crucially this list enumerates
# the themes we consider IN SCOPE for an agent lab, including ones we do NOT yet
# cover, so the coverage denominator is honest rather than self-selected. Verify
# against the current OWASP ASI publication before quoting these externally.
OWASP_ASI = {
    "ASI01": {
        "name": "Agent Goal Hijack",
        "covered": True,
        "where_in_lab": ["indirect_pi", "a4"],
        "student_learns": "Poisoned context / PI can redirect agent goals (silent export).",
    },
    "ASI02": {
        "name": "Tool Misuse and Exploitation",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "path_read", "a1", "a3", "a4"],
        "student_learns": "Tools are APIs; bad args = SQLi, path escape, exfil.",
    },
    "ASI03": {
        "name": "Identity / Privilege Abuse",
        "covered": True,
        "where_in_lab": ["a1", "a3", "m8"],
        "student_learns": "Unscoped access as privilege excess; policy-as-code gates by blast radius (Module 8).",
    },
    "ASI06": {
        "name": "Memory and Context Poisoning",
        "covered": True,
        "where_in_lab": ["a2", "indirect_pi"],
        "student_learns": "RAG/context stores can carry attacker instructions.",
    },
    "ASI04": {
        "name": "Resource Overload / Denial of Wallet",
        "covered": True,
        "where_in_lab": ["m11"],
        "student_learns": "Runaway plans and tool loops burn spend; budget + loop detection + rate limits (Module 11).",
    },
    "ASI05": {
        "name": "Cascading Hallucination / Unsupported Output",
        "covered": True,
        "where_in_lab": ["m10"],
        "student_learns": "Unsupported claims withheld; citations attribute poisoned sources (Module 10).",
    },
    "ASI07": {
        "name": "Insecure Inter-Agent Communication",
        "covered": True,
        "where_in_lab": ["a4", "m3"],
        "student_learns": "Unsigned inter-agent messages are tamperable; HMAC-sign + verify (Module 3).",
    },
    "ASI08": {
        "name": "Repudiation and Untraceability",
        "covered": True,
        "where_in_lab": ["m8"],
        "student_learns": "Queryable audit trail: who/what/decision/why/when for every action (Module 8).",
    },
    "ASI09": {
        "name": "Rogue Agents / Unverified Components",
        "covered": True,
        "where_in_lab": ["m3", "m7"],
        "student_learns": "Registry allow-listing plus signed capability manifests and startup attestation.",
    },
    # --- Honest gaps: in scope for an agent lab, not yet built. ---
    "ASI10": {
        "name": "Identity Spoofing and Impersonation",
        "covered": "partial",
        "where_in_lab": ["m3"],
        "student_learns": "Message signing gives integrity, but there is no per-agent identity/mTLS or delegated-auth model yet.",
    },
    "ASI11": {
        "name": "Overwhelming Human-in-the-Loop (approval fatigue)",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Not yet built: flooding the approver until they rubber-stamp is an unaddressed attack on control C5.",
    },
    "ASI12": {
        "name": "Unexpected Code Execution / RCE via tools",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Not yet built: the lab has no code-execution tool, so sandbox-escape is out of scope for now.",
    },
    "ASI13": {
        "name": "Human Manipulation and Deceptive Agent Behavior",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Not yet built: agents that mislead their operator require behavioural evaluation, not a deterministic check.",
    },
}

# Controls this lab teaches (defense catalog)
CONTROLS = [
    {
        "id": "C1",
        "name": "Parameterized / scoped DB access",
        "stops": ["direct_sqli", "exfil_chain", "a1", "a3", "a4"],
        "owasp": ["LLM02", "LLM06", "ASI02"],
        "lab_code": ["tools/db_tool/queries.py::query_secure", "defenses/m01/least_privilege.py"],
        "how": "Never concatenate user/model text into SQL. Use bound parameters and a fixed scope (e.g. customer_id).",
    },
    {
        "id": "C2",
        "name": "Tool argument schema allow-list",
        "stops": ["direct_sqli", "path_read", "a1", "a4"],
        "owasp": ["LLM06", "ASI02", "ASI07"],
        "lab_code": ["defenses/m01/schema_validation.py", "agents/executor.py"],
        "how": "At the executor, re-validate every tool name and arg shape. Reject free-form filter=1=1 and path '..'.",
    },
    {
        "id": "C3",
        "name": "Filesystem jail",
        "stops": ["path_read", "a1"],
        "owasp": ["LLM06", "ASI02"],
        "lab_code": ["tools/file_tool/server.py::_resolve_secure"],
        "how": "Resolve paths and enforce containment with Path.relative_to(workspace). Fail closed on escape.",
    },
    {
        "id": "C4",
        "name": "Email / egress allow-list",
        "stops": ["exfil_chain", "a3", "a4", "indirect_pi"],
        "owasp": ["LLM02", "ASI02"],
        "lab_code": ["tools/email_tool/server.py", "defenses/m01/least_privilege.py"],
        "how": "Only allow recipient domains you own (lab: example.test). Block external-logging.test style sinks.",
    },
    {
        "id": "C5",
        "name": "Human-in-the-loop for side effects",
        "stops": ["exfil_chain", "a3", "a4"],
        "owasp": ["LLM06", "ASI02"],
        "lab_code": ["defenses/m01/approval_gate.py"],
        "how": "Email, payments, file write default DENY unless a human (or LAB_APPROVE in the lab) approves.",
    },
    {
        "id": "C6",
        "name": "RAG trust / provenance filter",
        "stops": ["indirect_pi", "a2", "a4"],
        "owasp": ["LLM01", "LLM04", "LLM08", "ASI01", "ASI06"],
        "lab_code": ["rag/retriever.py", "rag/ingest.py metadata trust="],
        "how": "Tag corpus sources. Drop or quarantine trust=untrusted chunks before they enter the planner prompt.",
    },
    {
        "id": "C7",
        "name": "Never trust planner output as authorization",
        "stops": ["a4", "all tool attacks"],
        "owasp": ["LLM01", "LLM06", "ASI07"],
        "lab_code": ["agents/executor.py SECURE_MODE path"],
        "how": "Treat model plans as untrusted proposals. Policy lives in executor/tools, not in the system prompt alone.",
    },
    {
        "id": "C8", "name": "Content-based RAG poison detection",
        "stops": ["m2"], "owasp": ["LLM01", "LLM04", "LLM08", "ASI06"],
        "lab_code": ["defenses/m02/rag_detector.py"],
        "how": "Quarantine instruction-shaped chunks and collapse near-duplicate crowding; don't trust provenance labels.",
    },
    {
        "id": "C9", "name": "Authenticated inter-agent messages",
        "stops": ["m3"], "owasp": ["ASI07", "ASI01"],
        "lab_code": ["defenses/m03/signing.py"],
        "how": "HMAC-sign inter-agent messages; verify before acting so tampering is detected, not executed.",
    },
    {
        "id": "C10", "name": "Agent/tool registry allow-list",
        "stops": ["m3"], "owasp": ["ASI07", "LLM06"],
        "lab_code": ["defenses/m03/signing.py::registry_allows"],
        "how": "Only registered agents and tools may run; reject rogue components.",
    },
    {
        "id": "C11", "name": "Memory write validation",
        "stops": ["m4"], "owasp": ["ASI06", "LLM01"],
        "lab_code": ["defenses/m04/memory_guard.py::safe_write"],
        "how": "Memory stores facts, not commands; reject agent-directed instructions at write time.",
    },
    {
        "id": "C12", "name": "Memory provenance signing",
        "stops": ["m4"], "owasp": ["ASI06"],
        "lab_code": ["defenses/m04/memory_guard.py::safe_recall"],
        "how": "HMAC-tag entries on write; quarantine unsigned/tampered entries on recall.",
    },
    {
        "id": "C13", "name": "Measured guardrail pipeline",
        "stops": ["m5"], "owasp": ["LLM01", "LLM02", "LLM05"],
        "lab_code": ["guardrails/pipeline.py"],
        "how": "Scan input and output; benchmark catch rate, false-positive rate, and p50/p95 latency.",
    },
    {
        "id": "C14", "name": "Continuous red-team evaluation",
        "stops": ["all"], "owasp": ["LLM01", "LLM06", "ASI01", "ASI06", "ASI07"],
        "lab_code": ["tests/test_redteam_suite.py", ".github/workflows/redteam.yml"],
        "how": "Re-run every attack as a suite in CI; fail the build if attack-success rate regresses.",
    },
    {
        "id": "C15", "name": "Supply-chain attestation",
        "stops": ["m7"], "owasp": ["LLM03", "ASI02"],
        "lab_code": ["defenses/m07/attestation.py"],
        "how": "Signed capability manifests + startup attestation; refuse unverified or over-scoped tools.",
    },
    {
        "id": "C16", "name": "Policy-as-code decision matrix",
        "stops": ["m8"], "owasp": ["LLM06", "ASI02", "ASI03"],
        "lab_code": ["policy/engine.py"],
        "how": "Evaluate every action by blast radius (allow/deny/HITL); deny external egress by rule.",
    },
    {
        "id": "C17", "name": "Queryable audit trail",
        "stops": ["m8"], "owasp": ["ASI03", "ASI08"],
        "lab_code": ["policy/engine.py::audit_log"],
        "how": "Record who/what/decision/why/when for every action; queryable after the fact.",
    },
    {
        "id": "C18", "name": "System-prompt leak detection",
        "stops": ["m9"], "owasp": ["LLM07", "LLM01"],
        "lab_code": ["defenses/m09/prompt_leak.py"],
        "how": "Scan outbound responses for canary phrases and n-gram overlap with the system prompt; withhold on a hit. Damage control — keep secrets out of the prompt in the first place.",
    },
    {
        "id": "C19", "name": "Groundedness / citation enforcement",
        "stops": ["m10"], "owasp": ["LLM09", "LLM04", "ASI05"],
        "lab_code": ["defenses/m10/grounding.py"],
        "how": "Every claim must be supported by retrieved sources; withhold unsupported claims and cite the rest. Verifies support, not truth.",
    },
    {
        "id": "C20", "name": "Resource limits (denial of wallet)",
        "stops": ["m11"], "owasp": ["LLM10", "ASI04"],
        "lab_code": ["defenses/m11/limits.py"],
        "how": "Step cap + per-session cost budget + loop detection + rate limiting, scoped per identity.",
    },
]

# Per-attack remediation cards (student-facing)
REMEDIATIONS: dict[str, dict] = {
    "direct_sqli": {
        "attack": "Direct tool abuse — SQL dump",
        "root_cause": "db_tool accepts a raw SQL WHERE fragment and concatenates it into the query.",
        "impact": "Full table dump of synthetic customers (PII-like data).",
        "immediate_fix": [
            "Remove free-form `filter` from the tool schema.",
            "Only allow parameterized queries: WHERE customer_id = ? with int binding.",
            "Validate tool args in the executor before invoke (schema allow-list).",
        ],
        "secure_mode_does": "SECURE_MODE requires customer_id; rejects filter=1=1; returns error instead of rows.",
        "production_checklist": [
            "Least-privilege DB role (read only needed tables/rows).",
            "Row-level security / tenant id always from session, never from the model.",
            "Audit log every tool call with args + principal.",
        ],
        "controls": ["C1", "C2", "C7"],
        "owasp": ["LLM02", "LLM06", "ASI02"],
        "code": ["tools/db_tool/queries.py", "defenses/m01/schema_validation.py"],
    },
    "exfil_chain": {
        "attack": "Cross-tool exfiltration",
        "root_cause": "Unscoped read + unrestricted email recipient = data leaves the trust boundary.",
        "impact": "Customer dump emailed to attacker-controlled address (MailHog in the lab).",
        "immediate_fix": [
            "Block unscoped DB dumps (same as SQLi fix).",
            "Allow-list email domains; deny external by default.",
            "Require human approval for email_tool (HITL).",
        ],
        "secure_mode_does": "DB scope fails and/or email domain allow-list and/or approval_gate denies email.",
        "production_checklist": [
            "DLP on outbound tool channels.",
            "Separate 'read' tools from 'send' tools with different risk tiers.",
            "Rate limit and alert on bulk exports.",
        ],
        "controls": ["C1", "C4", "C5", "C7"],
        "owasp": ["LLM02", "LLM06", "ASI02"],
        "code": ["tools/email_tool/server.py", "defenses/m01/approval_gate.py"],
    },
    "indirect_pi": {
        "attack": "Indirect prompt injection via RAG",
        "root_cause": "Retrieved documents are treated as trusted instructions by the planner prompt.",
        "impact": "Benign user question can trigger hidden tool abuse after poison is retrieved.",
        "immediate_fix": [
            "Mark corpus sources with trust metadata.",
            "Filter untrusted chunks out of the planner context.",
            "Delimit untrusted text and instruct the model it is DATA not COMMANDS (defense in depth — still enforce C1–C5).",
        ],
        "secure_mode_does": "Retriever drops trust=untrusted; executor still blocks malicious tools if poison leaks.",
        "production_checklist": [
            "Content security on ingestion (review, signing, allow-listed sources).",
            "Separate system prompt from retrieved data with hard delimiters.",
            "Never let RAG override tool policy — policy is code, not prompt.",
        ],
        "controls": ["C6", "C7", "C1", "C4", "C5"],
        "owasp": ["LLM01", "LLM04", "LLM08", "ASI01", "ASI06"],
        "code": ["rag/retriever.py", "data/corpus/poisoned/doc_evil_001.txt", "agents/prompts/planner_system.txt"],
    },
    "path_read": {
        "attack": "Path traversal via file tool",
        "root_cause": "Naive path join without containment check.",
        "impact": "Read files outside the workspace jail (container FS).",
        "immediate_fix": [
            "Resolve path and enforce workspace root with relative_to / commonpath.",
            "Reject '..' segments at schema validation.",
            "Run file tools with minimal FS permissions.",
        ],
        "secure_mode_does": "Path jail raises PermissionError on escape attempts.",
        "production_checklist": [
            "Dedicated volume; no mount of host secrets.",
            "Prefer object storage with signed keys over raw FS tools.",
        ],
        "controls": ["C3", "C2"],
        "owasp": ["LLM06", "ASI02"],
        "code": ["tools/file_tool/server.py"],
    },
}


def curriculum_payload() -> dict:
    """API payload for UI + docs generators."""
    covered_llm = sum(1 for v in OWASP_LLM.values() if v["covered"] is True)
    partial_llm = sum(1 for v in OWASP_LLM.values() if v["covered"] == "partial")
    covered_asi = sum(1 for v in OWASP_ASI.values() if v["covered"] is True)
    partial_asi = sum(1 for v in OWASP_ASI.values() if v["covered"] == "partial")
    open_asi = [k for k, v in OWASP_ASI.items() if v["covered"] is False]

    return {
        "title": "AI Security curriculum map (this lab)",
        "mission": (
            "Students learn how AI agents are attacked (tool abuse, RAG injection, exfil) "
            "and how to remediate with controls outside the LLM — not by 'trusting the model'."
        ),
        "learning_outcomes": [
            "Explain agent architecture: user → RAG → planner (LLM) → executor → tools.",
            "Demonstrate SQLi/path/exfil via tools and indirect prompt injection via RAG.",
            "Map each attack to OWASP LLM Top 10 and Agentic ASI categories.",
            "Apply remediations: schema validation, least privilege, HITL, domain allow-lists, RAG trust filters.",
            "Prove SECURE_MODE changes outcomes (before/after) with evidence (SQL, MailHog, timeline).",
        ],
        "owasp_llm": OWASP_LLM,
        "owasp_asi": OWASP_ASI,
        "controls": CONTROLS,
        "remediations": REMEDIATIONS,
        "coverage_summary": {
            "llm_top10_full": covered_llm,
            "llm_top10_partial": partial_llm,
            "llm_top10_total": 10,
            "asi_full": covered_asi,
            "asi_partial": partial_asi,
            "asi_open": open_asi,
            "asi_listed": len(OWASP_ASI),
            "controls_taught": len(CONTROLS),
            "denominator_note": (
                "ASI ids are this lab's stable handles over published agentic threat "
                "themes, and the list includes themes we do NOT cover so the "
                "denominator is honest rather than self-selected."
            ),
        },
        "how_to_use_secure_mode": [
            "Run attack in VULNERABLE mode — observe exploit land (SQL / MailHog / plan).",
            "Set SECURE_MODE=true and recreate agent + tools.",
            "Re-run the same attack — read DEFENSE lines and remediation card.",
            "Open the control's lab_code files and match error messages to code.",
        ],
    }


def remediation_for(exploit_id: str) -> dict | None:
    return REMEDIATIONS.get(exploit_id)
