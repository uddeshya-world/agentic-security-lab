"""AI security curriculum: OWASP mapping, controls taught, remediations.

This is the "blue team / how to stop it" layer students need after red-team demos.
"""
from __future__ import annotations

# OWASP LLM Top 10 for Applications **2026** (renumbered 4 Aug 2026).
OWASP_LLM = {
    "LLM01": {
        "name": "Prompt Injection (direct & indirect)",
        "covered": True,
        "where_in_lab": ["direct_pi", "indirect_pi", "a2", "a4"],
        "student_learns": "Direct: the user prompt steers the planner. Indirect: retrieved docs become instructions.",
    },
    "LLM02": {
        "name": "Sensitive Information Disclosure",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "a3", "a4", "data_guards"],
        "student_learns": "Dump and email are disclosure. DLP classifies and masks/blocks the payload on four channels.",
    },
    "LLM03": {
        "name": "Excessive Agency",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "path_read", "a1", "a3", "a4", "direct_pi"],
        "student_learns": "Agent can call high-impact tools without enough authorization. (Was LLM06 in 2025.)",
    },
    "LLM04": {
        "name": "Supply Chain",
        "covered": True,
        "where_in_lab": ["m7"],
        "student_learns": "Rogue/tampered tools & MCP servers; signed manifests + attestation. (Was LLM03 in 2025.)",
    },
    "LLM05": {
        "name": "Data and Model Poisoning",
        "covered": True,
        "where_in_lab": ["indirect_pi", "a2", "m2"],
        "student_learns": "Poisoned corpus documents change agent behavior after retrieval. (Was LLM04 in 2025.)",
    },
    "LLM06": {
        "name": "Unbounded Consumption",
        "covered": True,
        "where_in_lab": ["m11"],
        "student_learns": "Denial of wallet: step cap + cost budget + loop detection + rate limit. (Was LLM10 in 2025.)",
    },
    "LLM07": {
        "name": "Misinformation",
        "covered": True,
        "where_in_lab": ["m10"],
        "student_learns": (
            "Groundedness/citation enforcement: unsupported claims are withheld. "
            "Scope: verifies SUPPORT BY SOURCES, not truth in general. (Was LLM09 in 2025.)"
        ),
    },
    "LLM08": {
        "name": "Hidden Context Exposure",
        "covered": True,
        "where_in_lab": ["m9"],
        "student_learns": "Leaked system prompt is recon (tool names, arg shapes). Detect on output; keep secrets out of the prompt. (Was LLM07 System Prompt Leakage in 2025.)",
    },
    "LLM09": {
        "name": "Vector and Embedding Weaknesses",
        "covered": True,
        "where_in_lab": ["a2", "indirect_pi", "m2"],
        "student_learns": "Retrieval can surface attacker-chosen chunks into context. (Was LLM08 in 2025.)",
    },
    "LLM10": {
        "name": "Improper Output Handling",
        "covered": True,
        "where_in_lab": ["m5", "data_guards"],
        "student_learns": "Output DLP masks PII/secrets before the user or a downstream tool sees them. (Was LLM05 in 2025.)",
    },
}

# Official OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10).
# Gaps are listed with covered=False so the denominator stays honest.
OWASP_ASI = {
    "ASI01": {
        "name": "Agent Goal Hijack",
        "covered": True,
        "where_in_lab": ["indirect_pi", "a4", "direct_pi"],
        "student_learns": "Poisoned context or a direct jailbreak can redirect agent goals (silent export).",
    },
    "ASI02": {
        "name": "Tool Misuse and Exploitation",
        "covered": True,
        "where_in_lab": ["direct_sqli", "exfil_chain", "path_read", "a1", "a3", "a4"],
        "student_learns": "Tools are APIs; bad args = SQLi, path escape, exfil.",
    },
    "ASI03": {
        "name": "Identity and Privilege Abuse",
        "covered": True,
        "where_in_lab": ["agent_identity", "a1", "m8"],
        "student_learns": "The agent's tool credential is not the user's authorization. Bind scope from the session principal.",
    },
    "ASI04": {
        "name": "Agentic Supply Chain Vulnerabilities",
        "covered": True,
        "where_in_lab": ["m7"],
        "student_learns": "Rogue/tampered tools and MCP servers; signed manifests + startup attestation.",
    },
    "ASI05": {
        "name": "Unexpected Code Execution (RCE)",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Out of scope: this lab has no code-execution tool. Adding one is a safety decision, not a checkbox.",
    },
    "ASI06": {
        "name": "Memory and Context Poisoning",
        "covered": True,
        "where_in_lab": ["a2", "indirect_pi", "m4", "m2"],
        "student_learns": "RAG and long-term memory are input channels. Validate on write; filter on retrieve.",
    },
    "ASI07": {
        "name": "Insecure Inter-Agent Communication",
        "covered": True,
        "where_in_lab": ["m3"],
        "student_learns": "Unsigned inter-agent messages are tamperable; HMAC-sign + verify.",
    },
    "ASI08": {
        "name": "Cascading Failures",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Not yet built: one bad tool result fanning out across a larger agent mesh.",
    },
    "ASI09": {
        "name": "Human-Agent Trust Exploitation",
        "covered": False,
        "where_in_lab": [],
        "student_learns": "Not yet built: HITL exists, but we do not yet attack the human (approval fatigue / social engineering of the operator).",
    },
    "ASI10": {
        "name": "Rogue Agents",
        "covered": True,
        "where_in_lab": ["m3", "m7"],
        "student_learns": "Registry allow-listing plus signed capability manifests and startup attestation.",
    },
}

# The agent data path, hop by hop, with the control that holds each one.
#
# This is the same eight-hop map `05-guardrail-map` teaches, lifted out of that
# scenario's markdown so the UI can render it without a second copy of the table
# living in a page. `tests/test_curriculum_2026.py` checks every `controls` entry
# here against CONTROLS, so a renamed control cannot silently orphan a hop.
#
# `stage` keys into the six-stage trace the UI already draws
# (user -> rag -> planner -> executor -> tools -> world), which is why several
# hops share a stage: the executor alone carries three distinct controls.
DATA_PATH_HOPS = [
    {
        "n": 1, "stage": "user", "name": "Input DLP",
        "threat": "SSN, card numbers or secrets typed straight into the prompt",
        "controls": ["C21"],
        "code": "guardrails/pipeline.py::scan_data(channel='input')",
    },
    {
        "n": 2, "stage": "rag", "name": "RAG + context DLP",
        "threat": "A retrieved document carries instructions, or PII, into the context",
        "controls": ["C6", "C21"],
        "code": "rag/retriever.py",
    },
    {
        "n": 3, "stage": "planner", "name": "Planner output",
        "threat": "The model authors a harmful plan and expects it to be obeyed",
        "controls": ["C7"],
        "code": "agents/executor.py",
    },
    {
        "n": 4, "stage": "executor", "name": "Identity",
        "threat": "Confused deputy: the agent spends its credential on the wrong principal",
        "controls": ["C1", "C7"],
        "code": "agents/executor.py (session customer_id)",
    },
    {
        "n": 5, "stage": "executor", "name": "Schema and arguments",
        "threat": "free-form filter=1=1, or ../ in a path",
        "controls": ["C2"],
        "code": "defenses/m01/schema_validation.py",
    },
    {
        "n": 6, "stage": "executor", "name": "Least privilege",
        "threat": "A read that was allowed to be far broader than the task needed",
        "controls": ["C1"],
        "code": "defenses/m01/least_privilege.py",
    },
    {
        "n": 7, "stage": "tools", "name": "Tool DLP, approval and egress",
        "threat": "PII in a tool result, an unattended send, a recipient you do not own",
        "controls": ["C21", "C5", "C4"],
        "code": "tools/email_tool/server.py, defenses/m01/approval_gate.py",
    },
    {
        "n": 8, "stage": "world", "name": "Output DLP",
        "threat": "The model recites the sensitive data back on its way out",
        "controls": ["C21"],
        "code": "guardrails/pipeline.py::scan_data(channel='output')",
    },
]

# Detection controls taught by the Blue Team Area (defense catalog, detection side).
# The `C` series is preventive -- it stops the attack. This `D` series is detective: it
# assumes the attack already ran and asks what recorded it, what separates it from normal
# traffic, and what the evidence does and does not prove. Blue Team scenarios cite these
# the way AI Security scenarios cite `C1`-`C21`.
DETECTIONS = [
    {
        "id": "D1",
        "name": "Know your recorders",
        "stops": [],
        "detects": ["exfil_chain", "a3"],
        "owasp": ["LLM02:2026", "ASI02"],
        "lab_code": ["lab/events.py", "tools/email_tool/server.py"],
        "how": (
            "Enumerate what actually writes a record before you hunt: the lab event log and "
            "the mail sink here. A gap in coverage is a finding, not a detail."
        ),
    },
    {
        "id": "D2",
        "name": "Chain-of-impact triage",
        "stops": [],
        "detects": ["exfil_chain", "a3"],
        "owasp": ["LLM02:2026", "LLM03:2026"],
        "lab_code": ["lab/events.py::list_events"],
        "how": (
            "Name every link -- what was read, by which tool, sent where, how much -- and "
            "corroborate each in a second source before it enters the timeline."
        ),
    },
    {
        "id": "D3",
        "name": "Detection specificity",
        "stops": [],
        "detects": ["exfil_chain"],
        "owasp": ["LLM03:2026", "ASI02"],
        "lab_code": ["lab/events.py", "guardrails/pipeline.py"],
        "how": (
            "Key the rule on the field that separates harmful from routine -- recipient "
            "domain and row count, not 'an email was sent'. A rule that fires on normal "
            "traffic is not a detection, it is noise."
        ),
    },
    {
        "id": "D4",
        "name": "Absence-of-evidence discipline",
        "stops": [],
        "detects": ["exfil_chain", "a3"],
        "owasp": ["LLM02:2026"],
        "lab_code": ["lab/runlog.py", "defenses/config.py"],
        "how": (
            "Re-run with the control on and state precisely what the empty sink proves: "
            "this payload, on this path, in this mode. It is not proof the control cannot "
            "be bypassed -- say so in the report."
        ),
    },
]

# Controls this lab teaches (defense catalog)
CONTROLS = [
    {
        "id": "C1",
        "name": "Parameterized / scoped DB access",
        "stops": ["direct_sqli", "exfil_chain", "a1", "a3", "a4"],
        "owasp": ["LLM02", "LLM03", "ASI02"],
        "lab_code": ["tools/db_tool/queries.py::query_secure", "defenses/m01/least_privilege.py"],
        "how": "Never concatenate user/model text into SQL. Use bound parameters and a fixed scope (e.g. customer_id).",
        "aisvs": [{"id": "C9.5.3", "strength": "demonstrates", "proven_by": ["18-agent-identity/step-03"]}, {"id": "C9.5.2", "strength": "partial"}],
    },
    {
        "id": "C2",
        "name": "Tool argument schema allow-list",
        "stops": ["direct_sqli", "path_read", "a1", "a4"],
        "owasp": ["LLM03", "ASI02", "ASI07"],
        "lab_code": ["defenses/m01/schema_validation.py", "agents/executor.py"],
        "how": "At the executor, re-validate every tool name and arg shape. Reject free-form filter=1=1 and path '..'.",
        "aisvs": [{"id": "C10.4.3", "strength": "partial"}, {"id": "C7.1.1", "strength": "partial"}],
    },
    {
        "id": "C3",
        "name": "Filesystem jail",
        "stops": ["path_read", "a1"],
        "owasp": ["LLM03", "ASI02"],
        "lab_code": ["tools/file_tool/server.py::_resolve_secure"],
        "how": "Resolve paths and enforce containment with Path.relative_to(workspace). Fail closed on escape.",
        "aisvs": [{"id": "C9.3.4", "strength": "partial"}],
    },
    {
        "id": "C4",
        "name": "Email / egress allow-list",
        "stops": ["exfil_chain", "a3", "a4", "indirect_pi"],
        "owasp": ["LLM02", "ASI02"],
        "lab_code": ["tools/email_tool/server.py", "defenses/m01/least_privilege.py"],
        "how": "Only allow recipient domains you own (lab: example.test). Block external-logging.test style sinks.",
        "aisvs": [{"id": "C7.3.3", "strength": "demonstrates", "proven_by": ["03-cross-tool-exfil/step-05"]}],
    },
    {
        "id": "C5",
        "name": "Human-in-the-loop for side effects",
        "stops": ["exfil_chain", "a3", "a4"],
        "owasp": ["LLM03", "ASI02"],
        "lab_code": ["defenses/m01/approval_gate.py"],
        "how": "Email, payments, file write default DENY unless a human (or LAB_APPROVE in the lab) approves.",
        "aisvs": [{"id": "C9.2.1", "strength": "partial"}, {"id": "C9.2.2", "strength": "partial"}, {"id": "C9.6.2", "strength": "partial"}],
    },
    {
        "id": "C6",
        "name": "RAG trust / provenance filter",
        "stops": ["indirect_pi", "a2", "a4"],
        "owasp": ["LLM01", "LLM05", "LLM09", "ASI01", "ASI06"],
        "lab_code": ["rag/retriever.py", "rag/ingest.py metadata trust="],
        "how": "Tag corpus sources. Drop or quarantine trust=untrusted chunks before they enter the planner prompt.",
        "aisvs": [{"id": "C2.1.3", "strength": "partial"}, {"id": "C12.5.4", "strength": "partial"}],
    },
    {
        "id": "C7",
        "name": "Never trust planner output as authorization",
        "stops": ["a4", "all tool attacks"],
        "owasp": ["LLM01", "LLM03", "ASI07"],
        "lab_code": ["agents/executor.py SECURE_MODE path"],
        "how": "Treat model plans as untrusted proposals. Policy lives in executor/tools, not in the system prompt alone.",
        "aisvs": [{"id": "C9.5.3", "strength": "demonstrates", "proven_by": ["16-direct-injection/step-03"]}, {"id": "C9.5.1", "strength": "partial"}],
    },
    {
        "id": "C8", "name": "Content-based RAG poison detection",
        "stops": ["m2"], "owasp": ["LLM01", "LLM05", "LLM09", "ASI06"],
        "lab_code": ["defenses/m02/rag_detector.py"],
        "how": "Quarantine instruction-shaped chunks and collapse near-duplicate crowding; don't trust provenance labels.",
        "aisvs": [{"id": "C2.1.3", "strength": "demonstrates", "proven_by": ["06-rag-deep-poisoning/step-04"]}, {"id": "C8.2.4", "strength": "partial"}],
    },
    {
        "id": "C9", "name": "Authenticated inter-agent messages",
        "stops": ["m3"], "owasp": ["ASI07", "ASI01"],
        "lab_code": ["defenses/m03/signing.py"],
        "how": "HMAC-sign inter-agent messages; verify before acting so tampering is detected, not executed.",
        "aisvs": [{"id": "C9.4.1", "strength": "partial"}, {"id": "C9.4.2", "strength": "partial"}, {"id": "C9.5.5", "strength": "partial"}],
    },
    {
        "id": "C10", "name": "Agent/tool registry allow-list",
        "stops": ["m3"], "owasp": ["ASI07", "LLM03"],
        "lab_code": ["defenses/m03/signing.py::registry_allows"],
        "how": "Only registered agents and tools may run; reject rogue components.",
        "aisvs": [{"id": "C9.3.7", "strength": "demonstrates", "proven_by": ["07-multi-agent/step-04"]}, {"id": "C10.1.2", "strength": "partial"}],
    },
    {
        "id": "C11", "name": "Memory write validation",
        "stops": ["m4"], "owasp": ["ASI06", "LLM01"],
        "lab_code": ["defenses/m04/memory_guard.py::safe_write"],
        "how": "Memory stores facts, not commands; reject agent-directed instructions at write time.",
        "aisvs": [{"id": "C8.2.3", "strength": "partial"}],
    },
    {
        "id": "C12", "name": "Memory provenance signing",
        "stops": ["m4"], "owasp": ["ASI06"],
        "lab_code": ["defenses/m04/memory_guard.py::safe_recall"],
        "how": "HMAC-tag entries on write; quarantine unsigned/tampered entries on recall.",
        "aisvs": [{"id": "C8.2.3", "strength": "partial"}, {"id": "C12.5.4", "strength": "partial"}],
    },
    {
        "id": "C13", "name": "Measured guardrail pipeline",
        "stops": ["m5"], "owasp": ["LLM01", "LLM02", "LLM10"],
        "lab_code": ["guardrails/pipeline.py"],
        "how": "Scan input and output; benchmark catch rate, false-positive rate, and p50/p95 latency.",
        "aisvs": [{"id": "C2.1.3", "strength": "demonstrates", "proven_by": ["09-guardrails/step-04"]}, {"id": "C12.2.1", "strength": "partial"}, {"id": "C12.1.2", "strength": "partial"}],
    },
    {
        "id": "C14", "name": "Continuous red-team evaluation",
        "stops": ["all"], "owasp": ["LLM01", "LLM03", "ASI01", "ASI06", "ASI07"],
        "lab_code": ["tests/test_redteam_suite.py", ".github/workflows/redteam.yml"],
        "how": "Re-run every attack as a suite in CI; fail the build if attack-success rate regresses.",
        "aisvs": [{"id": "C11.1.3", "strength": "partial"}],
    },
    {
        "id": "C15", "name": "Supply-chain attestation",
        "stops": ["m7"], "owasp": ["LLM04", "ASI02"],
        "lab_code": ["defenses/m07/attestation.py", "defenses/m07/manifest_pin.py"],
        "how": "Signed capability manifests + startup attestation; refuse unverified or over-scoped tools.",
        "aisvs": [{"id": "C10.4.8", "strength": "demonstrates", "proven_by": ["19-mcp-tool-poisoning/step-03"]}, {"id": "C6.2.2", "strength": "partial"}],
        "ast": ["AST02", "AST04", "AST07"],
    },
    {
        "id": "C16", "name": "Policy-as-code decision matrix",
        "stops": ["m8"], "owasp": ["LLM03", "ASI02", "ASI03"],
        "lab_code": ["policy/engine.py"],
        "how": "Evaluate every action by blast radius (allow/deny/HITL); deny external egress by rule.",
        "aisvs": [{"id": "C9.5.1", "strength": "demonstrates", "proven_by": ["12-governance/step-04"]}, {"id": "C9.5.3", "strength": "demonstrates", "proven_by": ["12-governance/step-04"]}],
    },
    {
        "id": "C17", "name": "Queryable audit trail",
        "stops": ["m8"], "owasp": ["ASI03", "ASI08"],
        "lab_code": ["policy/engine.py::audit_log"],
        "how": "Record who/what/decision/why/when for every action; queryable after the fact.",
        "aisvs": [{"id": "C12.4.2", "strength": "partial"}, {"id": "C12.1.2", "strength": "partial"}],
    },
    {
        "id": "C18", "name": "System-prompt leak detection",
        "stops": ["m9"], "owasp": ["LLM08", "LLM01"],
        "lab_code": ["defenses/m09/prompt_leak.py"],
        "how": "Scan outbound responses for canary phrases and n-gram overlap with the system prompt; withhold on a hit. Damage control — keep secrets out of the prompt in the first place.",
        "aisvs": [{"id": "C7.3.2", "strength": "demonstrates", "proven_by": ["13-prompt-leakage/step-04"]}],
    },
    {
        "id": "C19", "name": "Groundedness / citation enforcement",
        "stops": ["m10"], "owasp": ["LLM07", "LLM05"],
        "lab_code": ["defenses/m10/grounding.py"],
        "how": "Every claim must be supported by retrieved sources; withhold unsupported claims and cite the rest. Verifies support, not truth.",
        "aisvs": [{"id": "C7.4.1", "strength": "demonstrates", "proven_by": ["14-grounding/step-03"]}, {"id": "C7.4.3", "strength": "demonstrates", "proven_by": ["14-grounding/step-03"]}, {"id": "C7.4.2", "strength": "partial"}],
    },
    {
        "id": "C20", "name": "Resource limits (denial of wallet)",
        "stops": ["m11"], "owasp": ["LLM06"],
        "lab_code": ["defenses/m11/limits.py"],
        "how": "Step cap + per-session cost budget + loop detection + rate limiting, scoped per identity.",
        "aisvs": [{"id": "C9.1.2", "strength": "demonstrates", "proven_by": ["15-resource-limits/step-04"]}, {"id": "C9.1.1", "strength": "partial"}],
    },
    {
        "id": "C21",
        "name": "Data guards (four-channel DLP)",
        "stops": ["data_guards", "exfil_chain"],
        "owasp": ["LLM02", "LLM10"],
        "lab_code": ["guardrails/pipeline.py::scan_data"],
        "how": "Classify payload (public/confidential/restricted). Block SSN/PAN/secrets; mask emails. Apply on prompt, RAG, model output, and tool results — not only the destination.",
        "aisvs": [{"id": "C7.3.2", "strength": "demonstrates", "proven_by": ["17-data-guards/step-03"]}, {"id": "C8.2.1", "strength": "partial"}],
    },
    {
        "id": "C22",
        "name": "Skill permission manifest",
        "stops": ["poisoned_skill"],
        "owasp": ["LLM04", "ASI04"],
        "lab_code": ["defenses/m07/skill_manifest.py"],
        "how": "A skill declares the files and network it needs in its manifest; the runtime refuses anything undeclared, whatever the skill's prose says. A pattern scanner is not a substitute.",
        "aisvs": [{"id": "C9.3.3", "strength": "demonstrates", "proven_by": ["23-poisoned-skill/step-04"]}, {"id": "C9.3.4", "strength": "demonstrates", "proven_by": ["23-poisoned-skill/step-04"]}],
        "ast": ["AST01", "AST03", "AST05"],
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

    from lab import standards

    return {
        # AISVS v1.0 / Agentic Skills Top 10: versions and the chapters this lab does not
        # exercise, so the Area's honest-gaps table can list them without a second copy.
        "standards": {
            "aisvs_version": standards.AISVS_VERSION,
            "aisvs_url": standards.AISVS_URL,
            "aisvs_out_of_scope": [
                {"chapter": c, "name": standards.AISVS_CHAPTERS[c]["name"], "reason": r}
                for c, r in standards.AISVS_OUT_OF_SCOPE.items()
            ],
            "ast_version": standards.AST_VERSION,
        },
        "title": "AI Security curriculum map (this lab)",
        "mission": (
            "Students learn how AI agents are attacked (tool abuse, RAG injection, exfil) "
            "and how to remediate with controls outside the LLM — not by 'trusting the model'."
        ),
        "learning_outcomes": [
            "Explain agent architecture: user → RAG → planner (LLM) → executor → tools.",
            "Demonstrate SQLi/path/exfil, direct and indirect prompt injection, four-channel DLP, and confused-deputy identity.",
            "Map each attack to OWASP LLM Top 10 (2026) and ASI Top 10 (2026).",
            "Apply remediations: schema validation, session-bound identity, HITL, domain allow-lists, RAG trust filters, data guards.",
            "Prove SECURE_MODE changes outcomes (before/after) with evidence (SQL, MailHog, timeline).",
        ],
        "owasp_llm": OWASP_LLM,
        "owasp_asi": OWASP_ASI,
        "controls": CONTROLS,
        "detections": DETECTIONS,
        "data_path_hops": DATA_PATH_HOPS,
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
            "detections_taught": len(DETECTIONS),
            "denominator_note": (
                "ASI01–ASI10 are the official OWASP Agentic Top 10 (2026). "
                "Uncovered entries (ASI05 RCE, ASI08 cascading failures, ASI09 "
                "human-agent trust) stay listed so coverage is not self-selected. "
                "LLM ids are the 2026 list (Excessive Agency is LLM03, Hidden "
                "Context Exposure is LLM08)."
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
