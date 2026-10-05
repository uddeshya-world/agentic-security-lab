import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.graph import run_agent
from lab import content, credential, events, ledger, runlog
from lab.checks import run_check
from lab.exploits import get_exploit, list_exploits
from lab.lessons import get_lesson, get_lessons
from lab.simulate import run_simulation
from lab.status import collect_status
from observability.otel_setup import init_tracing
from rag.ingest import ingest_benign_corpus, ingest_poisoned_doc
from rag.retriever import retrieve

init_tracing()

# Hosted mode: the public catalog/demo. It serves read-only content and static
# UI only — the attack surface (live agent run, catalogued exploits, graded
# simulations that drive real tools, corpus ingestion) is REMOVED from the app,
# and the hosted compose ships no tool/ollama services at all. Two layers, so no
# single env-var mistake turns the demo into a public exploit host.
HOSTED = os.environ.get("LAB_HOSTED", "").lower() in ("1", "true", "yes")

POISON_DOC = Path("/data/corpus/poisoned/doc_evil_001.txt")
UI_DIR = Path(__file__).resolve().parents[1] / "lab" / "ui"


def _startup_ingest() -> None:
    try:
        n = ingest_benign_corpus()
        print(f"[startup] ingested {n} benign corpus docs", flush=True)
    except Exception as e:
        print(f"[startup] benign ingest skipped/failed: {e}", flush=True)


def _warm_ollama() -> None:
    """Load model weights so the first student attack is less likely to time out."""
    try:
        from agents.llm_client import chat

        chat([{"role": "user", "content": "Reply with OK only."}])
        print("[startup] ollama warm complete", flush=True)
    except Exception as e:
        print(f"[startup] ollama warm skipped/failed: {e}", flush=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not HOSTED:
        # Hosted mode has no tools or ollama to ingest into / warm.
        threading.Thread(target=_startup_ingest, name="benign-ingest", daemon=True).start()
        threading.Thread(target=_warm_ollama, name="ollama-warm", daemon=True).start()
    yield

app = FastAPI(
    title="CyberRange — Agentic Security Lab",
    description="CyberRange lesson engine + deliberately vulnerable agent lab. Start at /lab/ui/catalog.html",
    lifespan=lifespan,
)

if UI_DIR.is_dir():
    app.mount("/lab/ui", StaticFiles(directory=str(UI_DIR), html=True), name="lab-ui")


class RunRequest(BaseModel):
    session_id: str = "default"
    message: str
    seed_poison: bool = False


@app.get("/")
def root():
    # New experience: the Killercoda-style Areas catalog. The classic single-page
    # console is still available at /lab/ui/ (index.html).
    return RedirectResponse(url="/lab/ui/catalog.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/lab/ui/assets/favicon.svg")


@app.get("/health")
def health():
    from defenses.config import is_secure

    return {"status": "ok", "secure_mode": is_secure(), "lab_console": "/lab/ui/"}


@app.post("/run")
def run(req: RunRequest):
    """Live agent path: real Ollama planner → executor → tools."""
    events.clear_events()
    events.emit("plan", f"LIVE AGENT request: {req.message[:200]}", actor="user")

    if req.seed_poison:
        try:
            ingest_benign_corpus()
            if POISON_DOC.exists():
                pid = ingest_poisoned_doc(POISON_DOC)
                events.emit(
                    "retrieve",
                    f"Poison seeded into RAG for indirect PI drill (id={pid})",
                    actor="rag",
                    outcome="success",
                )
        except Exception as e:
            events.emit("retrieve", f"Poison seed failed: {e}", actor="rag", outcome="error")

    try:
        result = run_agent(req.session_id, req.message)
    except Exception as e:
        events.emit("result", f"Agent error: {e}", actor="planner", outcome="error")
        return {
            "ok": False,
            "error": str(e),
            "final_answer": None,
            "plan": [],
            "executor_results": [],
            "rag_context": [],
            "events": events.list_events(),
            "secure_mode": __import__("defenses.config", fromlist=["is_secure"]).is_secure(),
        }

    # Annotate plan + tool results into event log for the UI timeline
    for i, step in enumerate(result.get("plan") or []):
        events.emit(
            "plan",
            f"Planner step {i + 1}: tool={step.get('tool')} args={step.get('args')} reason={step.get('reason')}",
            actor="planner",
            detail=step,
            outcome="info",
        )
    for outcome in result.get("executor_results") or []:
        tool = outcome.get("tool")
        res = outcome.get("result")
        err = None
        sql = None
        if isinstance(res, dict):
            err = res.get("error")
            inner = res.get("result", res)
            if isinstance(inner, dict):
                err = err or inner.get("error")
                sql = inner.get("sql") or inner.get("would_have_been_sql")
        if sql:
            events.emit("sql", f"SQL: {sql}", actor=tool or "db_tool", detail={"sql": sql})
        if err:
            events.emit(
                "defense",
                f"Blocked/error on {tool}: {err}",
                actor="executor",
                outcome="blocked",
                detail=outcome,
            )
        else:
            events.emit(
                "tool",
                f"Executed {tool}",
                actor=tool or "executor",
                outcome="success",
                detail=outcome,
            )

    events.emit(
        "result",
        f"Agent finished. final_answer preview: {str(result.get('final_answer'))[:160]}",
        actor="planner",
        outcome="info",
    )

    from defenses.config import is_secure

    return {
        "ok": True,
        "final_answer": result["final_answer"],
        "plan": result["plan"],
        "executor_results": result["executor_results"],
        "rag_context": result["rag_context"],
        "events": events.list_events(),
        "secure_mode": is_secure(),
    }


@app.post("/lab/attack/{exploit_id}")
def lab_attack(exploit_id: str, session_id: str = "live-attack"):
    """Run a catalogued exploit against the live agent (Ollama), with executor fallback."""
    from lab.live_attack import run_live_or_executor_fallback

    return run_live_or_executor_fallback(exploit_id, session_id=session_id)

# --- Lesson engine APIs (Killercoda-style catalog + stepper + checks) ---


@app.get("/catalog")
def catalog():
    """Areas + scenarios for the catalog page."""
    return content.catalog_payload()


@app.get("/scenario/{area_id}/{scenario_id}")
def scenario(area_id: str, scenario_id: str):
    """Full scenario for the stepper: metadata + ordered steps with rendered bodies."""
    payload = content.scenario_payload(area_id, scenario_id)
    if not payload:
        return {"error": "not found", "area_id": area_id, "scenario_id": scenario_id}
    return payload


class CheckRequest(BaseModel):
    # Optional client hint; the graded check still forces its own require_mode.
    session_id: str = "stepper"
    # Answer to a `recall` question. Graded server-side — the key never ships to
    # the browser, so the answer is not one View-Source away.
    answer: str | int | None = None


@app.post("/scenario/{area_id}/{scenario_id}/check/{step_id}")
def scenario_check(area_id: str, scenario_id: str, step_id: str, _req: CheckRequest | None = None):
    """Run a step's verification and return pass/fail with lab-state evidence."""
    step = content.get_step(area_id, scenario_id, step_id)
    if step is None:
        return {"ok": False, "passed": False, "message": "step not found", "kind": "error"}
    check = step.get("check")
    result = run_check(
        check,
        answer=(_req.answer if _req else None),
        step_key=f"{area_id}/{scenario_id}/{step_id}",
    )
    # The badge is built from this ledger, so only a pass graded here counts.
    if check and result.get("passed"):
        ledger.record_pass(area_id, scenario_id, step_id, check.get("kind"), check.get("require_mode"))
    return result


class CredentialRequest(BaseModel):
    learner: str | None = None
    # The browser's record of which graded checks passed. Only used to explain a
    # mismatch; the badge is graded and signed from the server-side ledger.
    passed: list[dict] = []


@app.get("/credential/{area_id}/requirements")
def credential_requirements(area_id: str):
    """Every graded check an Area requires — so the UI can show what is still open."""
    return {"area_id": area_id, "required": credential.required_checks(area_id)}


@app.post("/credential/{area_id}/issue")
def credential_issue(area_id: str, req: CredentialRequest | None = None):
    """Issue a signed, transcript-backed completion badge — or say what is missing."""
    req = req or CredentialRequest()
    return credential.issue(area_id, req.learner, req.passed)


@app.get("/credential/verify")
def credential_verify(token: str):
    """Check a badge's signature against this instance's key."""
    return credential.verify_token(token)


@app.post("/lab/content/reload")
def content_reload():
    """Drop the content parse cache so edited scenarios load without a restart."""
    content.reload()
    return {"reloaded": True, **content.catalog_payload()}


# --- Lab APIs ---


@app.get("/lab/status")
def lab_status():
    return collect_status()


@app.get("/lab/exploits")
def lab_exploits():
    return list_exploits()


@app.get("/lab/curriculum")
def lab_curriculum():
    """OWASP map, controls taught, remediations — blue-team half of the course."""
    from lab.curriculum import curriculum_payload

    return curriculum_payload()


@app.get("/lab/remediation/{exploit_id}")
def lab_remediation(exploit_id: str):
    from lab.curriculum import remediation_for

    r = remediation_for(exploit_id)
    if not r:
        return {"error": "not found", "exploit_id": exploit_id}
    return r


@app.get("/lab/lessons")
def lab_lessons():
    return get_lessons()


@app.get("/lab/lessons/{lesson_id}")
def lab_lesson(lesson_id: str):
    lesson = get_lesson(lesson_id)
    if not lesson:
        return {"error": "not found"}
    return lesson


@app.get("/lab/events")
def lab_events(since_id: int = 0, limit: int = 200):
    return {"events": events.list_events(since_id=since_id, limit=limit)}


@app.delete("/lab/events")
def lab_events_clear():
    events.clear_events()
    return {"cleared": True}


@app.post("/lab/simulate/{lesson_id}")
def lab_simulate(lesson_id: str, secure: bool | None = None, step: str | None = None):
    """Deterministic teaching sims (still real tools). Prefer /lab/attack for live LLM.

    ``secure`` forces the mode for this run only (used by the guided stepper to
    show vuln vs secure without recreating containers); omit to use the
    container's SECURE_MODE.

    The outcome is recorded in ``lab.runlog`` so a step's Check can grade the run
    the student performed instead of quietly performing it for them.
    """
    run = run_simulation(lesson_id, clear=True, secure=secure)
    if run.get("ok"):
        from defenses.config import is_secure

        effective = is_secure() if secure is None else bool(secure)
        runlog.record(
            lesson_id, effective, run.get("result") or {}, len(run.get("events") or []), step_key=step
        )
    return run


@app.post("/lab/ingest-benign")
def lab_ingest_benign():
    return {"ingested": ingest_benign_corpus()}


@app.post("/lab/ingest-poisoned")
def lab_ingest_poisoned():
    if not POISON_DOC.exists():
        return {"error": f"poison fixture missing: {POISON_DOC}"}
    doc_id = ingest_poisoned_doc(POISON_DOC)
    return {"ingested_id": doc_id, "path": str(POISON_DOC)}


@app.get("/lab/retrieve")
def lab_retrieve(q: str, top_k: int = 3):
    docs = retrieve(q, top_k=top_k)
    return {"query": q, "documents": docs, "count": len(docs)}


# --- Hosted-mode hardening: physically remove the attack surface -------------
# In hosted mode these routes are dropped from the served app entirely (not just
# gated), so the public demo cannot run the agent, catalogued exploits, graded
# simulations, or corpus ingestion even if the tool services were somehow present.
SENSITIVE_PATHS = {
    "/run",
    "/lab/attack/{exploit_id}",
    "/lab/simulate/{lesson_id}",
    "/scenario/{area_id}/{scenario_id}/check/{step_id}",
    "/lab/ingest-benign",
    "/lab/ingest-poisoned",
    "/lab/retrieve",
    "/lab/content/reload",
    # Issuing mints a signed badge from a client-supplied list of passes. On a
    # public deploy that is a badge vending machine, which is exactly the
    # credibility the credential design exists to protect. `/requirements` and
    # `/verify` stay: both are read-only, and the public verify page needs them.
    "/credential/{area_id}/issue",
}

if HOSTED:
    app.router.routes = [
        r for r in app.router.routes if getattr(r, "path", None) not in SENSITIVE_PATHS
    ]
