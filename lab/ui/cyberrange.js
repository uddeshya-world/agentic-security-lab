/* ==========================================================================
   CyberRange — shared behaviour
   --------------------------------------------------------------------------
   The blast trace is the only non-obvious thing in here. It reads the event log
   a run left behind and answers one question: how far did this get, and what
   stopped it. Same instrument on the landing page and on every scenario, so the
   thing you learn to read on page one is the thing you read for the next four
   hours.
   ========================================================================== */

const CR = (() => {
  const STAGES = ["user", "rag", "planner", "executor", "tools", "world"];
  const STAGE_LABEL = ["USER", "RAG", "PLANNER", "EXECUTOR", "TOOLS", "WORLD"];

  // Which stage an event proves the run reached.
  const PHASE_STAGE = {
    user: 0, prompt: 0,
    retrieve: 1, rag: 1,
    plan: 2,
    tool: 3, invoke: 3,
    sql: 4, file: 4, email: 4,
    result: 5, exfil: 5,
  };

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      ...opts,
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    if (!res.ok) throw new Error(data.error || data.detail || res.statusText);
    return data;
  }

  /* ---- progress (this browser only; the badge is explicit about that) ---- */
  const progKey = (area, scen) => `cr:progress:${area}:${scen}`;

  function loadProgress(area, scen) {
    try { return JSON.parse(localStorage.getItem(progKey(area, scen)) || "{}"); }
    catch { return {}; }
  }
  function saveProgress(area, scen, p) {
    try { localStorage.setItem(progKey(area, scen), JSON.stringify(p)); } catch { /* private mode */ }
  }
  /** Record a pass with enough detail to become a transcript row later. */
  function recordPass(area, scen, stepId, kind, mode) {
    const p = loadProgress(area, scen);
    p[stepId] = { passed: true, kind: kind || "manual", mode: mode || "any", at: new Date().toISOString() };
    saveProgress(area, scen, p);
  }
  const isPassed = (p, stepId) => !!(p[stepId] && (p[stepId] === true || p[stepId].passed));

  /** Every recorded pass across an Area, shaped for POST /credential/{area}/issue. */
  function transcript(area, scenarios) {
    const rows = [];
    for (const s of scenarios) {
      const p = loadProgress(area, s.id);
      for (const [stepId, v] of Object.entries(p)) {
        if (!isPassed(p, stepId)) continue;
        rows.push({ scenario: s.id, step: stepId, kind: v.kind || "manual", mode: v.mode || "any" });
      }
    }
    return rows;
  }

  /* ---- the blast trace ---- */

  /** Build the markup once; call `paint` to update it. */
  function traceHTML(caption = "No run recorded yet.") {
    return `
      <div class="track"><div class="flow"></div><div class="stopmark"></div></div>
      <div class="stages">${STAGE_LABEL.map((s, i) => {
        const pct = (i / (STAGE_LABEL.length - 1)) * 100;
        const shift = i === 0 ? "0" : i === STAGE_LABEL.length - 1 ? "-100%" : "-50%";
        return `<span style="left:${pct}%;transform:translateX(${shift})">${s}</span>`;
      }).join("")}</div>
      <div class="caption">${esc(caption)}</div>`;
  }

  /**
   * Read a run and paint how far it travelled.
   * @param {HTMLElement} el   an element with class `trace`
   * @param {Array} events     the run's event log
   * @param {Object} result    the run's result ({success, blocked, detail})
   */
  function paintTrace(el, events, result) {
    if (!el) return;
    events = events || [];
    result = result || {};

    let reachedIdx = 0;
    let defenseAt = null;
    let defenseMsg = "";

    for (const e of events) {
      const phase = (e.phase || "").toLowerCase();

      if (phase === "defense" || phase === "guardrail") {
        // Only the first DEFENSE line that actually stops something marks the
        // containment point. The sims also emit DEFENSE rows announcing which
        // mode each tool is in, and a closing summary of the controls that were
        // active — neither of those stopped anything.
        if (defenseAt === null && isBlockingDefense(e.message || "")) {
          defenseAt = reachedIdx;
          defenseMsg = e.message;
        }
        continue;
      }

      // A `result` row is written whether the attack landed or was stopped, so
      // it only proves the run reached the world when the run actually succeeded.
      if (phase === "result" && !result.success) continue;

      const idx = PHASE_STAGE[phase];
      if (idx !== undefined && idx > reachedIdx && defenseAt === null) reachedIdx = idx;
    }
    if (result.success) reachedIdx = STAGES.length - 1;

    // Containment is the run's own verdict, not the presence of a DEFENSE line.
    const blocked = !!result.blocked;
    if (blocked && defenseAt !== null) reachedIdx = Math.max(defenseAt, 1);

    const reach = reachedIdx / (STAGES.length - 1);
    el.style.setProperty("--reach", String(reach));
    el.classList.toggle("contained", blocked);
    el.classList.toggle("hot", !blocked && !!result.success);

    el.querySelectorAll(".stages span").forEach((sp, i) => {
      sp.classList.toggle("reached", i <= reachedIdx && !(blocked && i === reachedIdx));
      sp.classList.toggle("stopped", blocked && i === reachedIdx);
    });

    const cap = el.querySelector(".caption");
    if (!cap) return;
    if (blocked) {
      const control = defenseMsg ? shortControl(defenseMsg) : "a control";
      cap.innerHTML = `Contained at <b>${esc(STAGE_LABEL[reachedIdx])}</b> — ${esc(control)}`;
    } else if (result.success) {
      cap.innerHTML = `Reached <b>WORLD</b> — ${esc(result.detail || "the attack completed")}`;
    } else {
      cap.innerHTML = `Ran to <b>${esc(STAGE_LABEL[reachedIdx])}</b>. Nothing was blocked and nothing landed.`;
    }
  }

  /** Did this DEFENSE line stop something, or is it just describing the setup? */
  function isBlockingDefense(msg) {
    if (/^\s*active\s*:/i.test(msg)) return false;          // closing summary of controls
    if (/\bis in\b.*\bmode\b/i.test(msg)) return false;      // "db_tool is in VULNERABLE mode"
    return /block|refus|denied|reject|quarantin|stopped|withheld|guardrail|jail/i.test(msg);
  }

  /** Pull the control's name out of a DEFENSE line so the caption stays short. */
  function shortControl(msg) {
    const paren = msg.match(/\(([^)]+)\)/);
    if (paren) return paren[1];
    const colon = msg.split(":")[0];
    return (colon.length < 60 ? colon : msg.slice(0, 60)).trim();
  }

  /* ---- code blocks ---- */
  function enhanceCode(root, onSendToTerminal) {
    root.querySelectorAll("pre").forEach((pre) => {
      const code = pre.querySelector("code");
      if (!code || pre.querySelector(".codebar")) return;
      const bar = document.createElement("div");
      bar.className = "codebar";

      const copy = document.createElement("button");
      copy.type = "button";
      copy.textContent = "Copy";
      copy.onclick = () => {
        navigator.clipboard?.writeText(code.innerText);
        copy.textContent = "Copied";
        setTimeout(() => (copy.textContent = "Copy"), 1200);
      };
      bar.appendChild(copy);

      if (onSendToTerminal && /^\s*(curl|docker|SECURE_MODE|cat|pip|python|ls|jq)\b/m.test(code.innerText)) {
        const send = document.createElement("button");
        send.type = "button";
        send.textContent = "To terminal";
        send.onclick = () => onSendToTerminal(code.innerText);
        bar.appendChild(send);
      }
      pre.appendChild(bar);
    });
    // Wide tables scroll inside themselves rather than pushing the page sideways.
    root.querySelectorAll("table").forEach((t) => {
      if (t.parentElement?.classList.contains("tablewrap")) return;
      const wrap = document.createElement("div");
      wrap.className = "tablewrap";
      t.replaceWith(wrap);
      wrap.appendChild(t);
    });
  }

  return { STAGES, STAGE_LABEL, esc, api, loadProgress, saveProgress, recordPass, isPassed,
           transcript, traceHTML, paintTrace, enhanceCode };
})();
