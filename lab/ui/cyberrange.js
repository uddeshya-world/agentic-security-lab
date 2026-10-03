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

  /* ------------------------------------------------------------------------
     The scope strip. Two jobs, and the second is the reason it exists: it
     reports whether the defenses are currently on, read from /health rather
     than asserted in markup. A learner who forgot they left SECURE_MODE on
     otherwise spends a scenario wondering why the attack will not land.

     Dismissal is per-tab (sessionStorage), not permanent -- the estate being
     synthetic is worth restating on a fresh visit.
     ------------------------------------------------------------------------ */
  const ANNOUNCE_KEY = "cr.announce.dismissed";

  function initAnnounce() {
    const el = document.querySelector(".cr-announce");
    if (!el) return;

    let dismissed = false;
    try { dismissed = sessionStorage.getItem(ANNOUNCE_KEY) === "1"; } catch { /* private mode */ }
    if (dismissed) { el.hidden = true; return; }

    const close = el.querySelector(".x");
    if (close) close.addEventListener("click", () => {
      el.hidden = true;
      try { sessionStorage.setItem(ANNOUNCE_KEY, "1"); } catch { /* private mode */ }
    });

    // The live half. No spinner and no error state: if /health does not answer,
    // the strip simply keeps its static half and says nothing it cannot back up.
    const mode = el.querySelector(".mode");
    if (!mode) return;
    api("/health").then((h) => {
      const secure = !!h.secure_mode;
      mode.classList.add("is-known");
      mode.classList.toggle("secure", secure);
      const label = mode.querySelector(".t");
      if (label) label.textContent = secure ? "secure mode on" : "secure mode off";
      mode.title = secure
        ? "Defenses are enabled. Attacks in the lessons are expected to be contained."
        : "Defenses are disabled. Attacks in the lessons are expected to land.";
    }).catch(() => { /* the lab may not be running yet; stay quiet */ });
  }

  /* ---- progress (this browser only; the badge is explicit about that) ---- */

  /* ------------------------------------------------------------------------
     Theme. Dark is this product's design, so "no stored choice" means follow
     the system and the CSS handles that on its own -- we only ever stamp
     data-theme when the user has actually chosen, which is what lets an
     explicit choice beat the system preference in both directions.
     ------------------------------------------------------------------------ */
  const THEME_KEY = "cr:theme";

  function storedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch { return null; }
  }

  /** What the page is showing right now, chosen or inherited. */
  function activeTheme() {
    const stored = storedTheme();
    if (stored === "light" || stored === "dark") return stored;
    try {
      return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    } catch { return "dark"; }
  }

  function applyTheme(mode) {
    const root = document.documentElement;
    if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
  }

  function setTheme(mode) {
    applyTheme(mode);
    try { localStorage.setItem(THEME_KEY, mode); } catch { /* private mode */ }
    document.querySelectorAll(".cr-theme").forEach((b) =>
      b.setAttribute("aria-label", mode === "light" ? "Switch to dark theme" : "Switch to light theme"));
  }

  const SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
              'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/>' +
              '<path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4' +
              'M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>';
  const MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
               '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function initTheme() {
    // Re-apply the stored choice on every page so navigation does not flash.
    const stored = storedTheme();
    if (stored) applyTheme(stored);

    document.querySelectorAll(".cr-theme").forEach((btn) => {
      if (!btn.querySelector("svg")) btn.innerHTML = SUN + MOON;
      btn.setAttribute("aria-label",
        activeTheme() === "light" ? "Switch to dark theme" : "Switch to light theme");
      btn.addEventListener("click", () => setTheme(activeTheme() === "light" ? "dark" : "light"));
    });
  }

  /* ------------------------------------------------------------------------
     Search. An inline input in the nav overflows between 720px and ~1000px
     once there are five links, so this is an overlay instead: a button in the
     nav opens it, "/" opens it from anywhere, Escape closes it.

     It searches the /catalog payload the page already has to fetch -- scenario
     title, summary, Area, OWASP ids and control ids -- so there is no backend
     and no second source of truth to drift.
     ------------------------------------------------------------------------ */
  let searchIndex = null;
  let searchEl = null;

  function buildSearchIndex(areas) {
    const rows = [];
    for (const a of areas || []) {
      for (const s of a.scenarios || []) {
        const owasp = (s.owasp || []).map(owaspLabel);
        rows.push({
          area: a.id,
          areaTitle: a.title || a.id,
          locked: a.status !== "available",
          id: s.id,
          title: s.title || s.id,
          summary: s.summary || "",
          track: s.track || "core",
          owasp: owasp,
          controls: s.controls || [],
          // One lowercased haystack so matching is a single indexOf per row.
          hay: [s.id, s.title, s.summary, a.title, (s.owasp || []).join(" "),
                (s.controls || []).join(" "), s.track].join(" ").toLowerCase(),
        });
      }
    }
    return rows;
  }

  function searchRank(rows, q) {
    const needle = q.trim().toLowerCase();
    if (!needle) return [];
    const terms = needle.split(/\s+/).filter(Boolean);
    const out = [];
    for (const r of rows) {
      let score = 0, all = true;
      for (const t of terms) {
        if (r.hay.indexOf(t) === -1) { all = false; break; }
        // A title hit is worth more than a body hit, and an id hit most of all.
        if (r.id.toLowerCase().indexOf(t) !== -1) score += 6;
        if (r.title.toLowerCase().indexOf(t) !== -1) score += 4;
        if (r.owasp.join(" ").toLowerCase().indexOf(t) !== -1) score += 3;
        if (r.controls.join(" ").toLowerCase().indexOf(t) !== -1) score += 3;
        score += 1;
      }
      if (all) out.push({ r, score });
    }
    out.sort((a, b) => b.score - a.score || a.r.id.localeCompare(b.r.id));
    return out.slice(0, 12).map((x) => x.r);
  }

  function searchResultsHTML(rows, q) {
    if (!q.trim()) {
      return '<div class="cr-sr-empty">Search scenarios by name, OWASP id (try <b>LLM03</b>), ' +
             'control (<b>C21</b>), or track (<b>core</b>).</div>';
    }
    if (!rows.length) {
      return '<div class="cr-sr-empty">Nothing matches <b>' + esc(q) + '</b>.</div>';
    }
    return rows.map((r, i) => {
      const chips = (r.locked ? ['<span class="tag warn">authoring</span>'] : [])
        .concat(r.owasp.slice(0, 3)
          .map((o) => '<span class="tag quiet">' + esc(owaspId(o)) + "</span>")).join("");
      const href = "/lab/ui/scenario.html?area=" + encodeURIComponent(r.area) +
                   "&id=" + encodeURIComponent(r.id);
      return '<a class="cr-sr-row" role="option" data-i="' + i + '" href="' + href + '">' +
               '<span class="cr-sr-main">' +
                 '<span class="cr-sr-title">' + esc(r.title) + "</span>" +
                 '<span class="cr-sr-sub">' + esc(r.areaTitle) + " · " + esc(r.id) + "</span>" +
               "</span>" +
               '<span class="cr-sr-chips">' + chips + "</span>" +
             "</a>";
    }).join("");
  }

  function openSearch() {
    if (!searchEl) return;
    searchEl.hidden = false;
    document.body.style.overflow = "hidden";
    const input = searchEl.querySelector("input");
    if (input) { input.value = ""; input.focus(); }
    searchEl.querySelector(".cr-sr-list").innerHTML = searchResultsHTML([], "");
    document.querySelectorAll(".cr-search-btn").forEach((b) => b.setAttribute("aria-expanded", "true"));
  }

  function closeSearch() {
    if (!searchEl) return;
    searchEl.hidden = true;
    document.body.style.overflow = "";
    document.querySelectorAll(".cr-search-btn").forEach((b) => b.setAttribute("aria-expanded", "false"));
  }

  function initSearch() {
    const btns = document.querySelectorAll(".cr-search-btn");
    if (!btns.length) return;

    searchEl = document.createElement("div");
    searchEl.className = "cr-search";
    searchEl.hidden = true;
    searchEl.innerHTML =
      '<div class="cr-sr-backdrop"></div>' +
      '<div class="cr-sr-panel" role="dialog" aria-modal="true" aria-label="Search scenarios">' +
        '<input type="search" placeholder="Search scenarios, OWASP ids, controls" ' +
               'autocomplete="off" spellcheck="false" aria-label="Search scenarios" />' +
        '<div class="cr-sr-list" role="listbox"></div>' +
        '<div class="cr-sr-foot"><span><kbd>Esc</kbd> close</span><span id="crSrCount"></span></div>' +
      "</div>";
    document.body.appendChild(searchEl);

    const input = searchEl.querySelector("input");
    const list = searchEl.querySelector(".cr-sr-list");
    const count = searchEl.querySelector("#crSrCount");

    async function ensureIndex() {
      if (searchIndex) return searchIndex;
      try {
        const cat = await api("/catalog");
        searchIndex = buildSearchIndex(cat.areas || []);
      } catch (e) {
        searchIndex = [];
      }
      return searchIndex;
    }

    btns.forEach((b) => b.addEventListener("click", async () => {
      openSearch();
      await ensureIndex();
    }));

    input.addEventListener("input", async () => {
      const rows = await ensureIndex();
      const q = input.value;
      const hits = searchRank(rows, q);
      list.innerHTML = searchResultsHTML(hits, q);
      count.textContent = q.trim() ? hits.length + " of " + rows.length : rows.length + " scenarios";
    });

    // Enter opens the first hit -- the common case is "type three letters, go".
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const first = list.querySelector(".cr-sr-row");
        if (first) { e.preventDefault(); window.location.href = first.getAttribute("href"); }
      }
    });

    searchEl.querySelector(".cr-sr-backdrop").addEventListener("click", closeSearch);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !searchEl.hidden) { closeSearch(); return; }
      // "/" is the conventional shortcut, but not while the user is typing.
      const tag = (e.target && e.target.tagName || "").toLowerCase();
      const typing = tag === "input" || tag === "textarea" || (e.target && e.target.isContentEditable);
      if (e.key === "/" && !typing && searchEl.hidden) {
        e.preventDefault();
        openSearch();
        ensureIndex();
      }
    });
  }

  /* ------------------------------------------------------------------------
     Scroll narrative.

     Everything below is an ENHANCEMENT and is written to be deletable. GSAP,
     ScrollTrigger and Lenis are vendored in lab/ui/vendor/, and if that
     directory is missing -- or the browser asks for reduced motion -- these all
     return early and the page keeps the IntersectionObserver reveal system it
     already had. The hop diagram in particular is authored as a readable static
     figure first; the scrub is layered on top of something that already works.
     ------------------------------------------------------------------------ */
  function hasGsap() {
    return typeof window !== "undefined" && window.gsap && window.ScrollTrigger;
  }

  /** Smooth scrolling, marketing-shaped pages only.
      The player and the sandbox console have their own scrolling panes and
      hijacking the document scroll under them feels broken, so they opt out by
      simply never calling this. */
  function initSmoothScroll() {
    if (prefersReducedMotion()) return null;
    if (typeof window === "undefined" || !window.Lenis) return null;
    try {
      const lenis = new window.Lenis({ duration: 0.9, smoothWheel: true });
      function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
      requestAnimationFrame(raf);
      if (hasGsap()) {
        lenis.on("scroll", window.ScrollTrigger.update);
        window.ScrollTrigger.refresh();
      }
      return lenis;
    } catch (e) { return null; }
  }

  /* ---- the hop diagram ---------------------------------------------------
     Renders `data_path_hops` from /lab/curriculum. Static and complete on
     first paint: every hop visible, every control named. The scrub only
     changes which hop is *emphasised*, so a user who never scrolls, or who
     asked for reduced motion, still reads the whole thing.
     --------------------------------------------------------------------- */
  function renderHops(mount, hops, controlsById) {
    if (!mount || !hops || !hops.length) return;
    mount.innerHTML = hops.map((h, i) => {
      const ctrls = (h.controls || []).map((c) => {
        const meta = controlsById[c];
        return '<span class="hop-c" title="' + esc(meta ? meta.name : c) + '">' + esc(c) + "</span>";
      }).join("");
      return (
        '<li class="hop" data-hop="' + i + '" data-stage="' + esc(h.stage) + '">' +
          '<span class="hop-n">' + String(h.n).padStart(2, "0") + "</span>" +
          '<span class="hop-body">' +
            '<span class="hop-name">' + esc(h.name) + "</span>" +
            '<span class="hop-threat">' + esc(h.threat) + "</span>" +
            '<span class="hop-code">' + esc(h.code) + "</span>" +
          "</span>" +
          '<span class="hop-ctrls">' + ctrls + "</span>" +
        "</li>"
      );
    }).join("");
  }

  /** Scrub the emphasis through the hops as the section passes.
      No pinning: a pinned section traps the reader on a short viewport, and the
      diagram reads fine unpinned. */
  function initHopScrub(section) {
    if (!section) return;
    const items = [...section.querySelectorAll(".hop")];
    if (!items.length) return;

    // Static fallback: everything legible, nothing dimmed.
    if (prefersReducedMotion() || !hasGsap()) {
      items.forEach((el) => el.classList.add("is-lit"));
      return;
    }

    const gsap = window.gsap;
    gsap.registerPlugin(window.ScrollTrigger);

    window.ScrollTrigger.create({
      trigger: section,
      start: "top 72%",
      end: "bottom 40%",
      scrub: 0.4,
      onUpdate: (self) => {
        const upto = Math.round(self.progress * items.length);
        items.forEach((el, i) => el.classList.toggle("is-lit", i < Math.max(1, upto)));
        const bar = section.querySelector(".hop-rail i");
        if (bar) bar.style.height = (self.progress * 100).toFixed(1) + "%";
      },
      onLeave: () => items.forEach((el) => el.classList.add("is-lit")),
      // Scrolling back up past the section must not leave it dark.
      onLeaveBack: () => items.forEach((el, i) => el.classList.toggle("is-lit", i === 0)),
    });

    items.forEach((el, i) => el.classList.toggle("is-lit", i === 0));
  }

  /** Masked, staggered reveal for a heading -- one word at a time out from
      behind a clipping edge. Falls back to the plain reveal system. */
  function initWordReveal(el) {
    if (!el || el.dataset.wordsDone === "1") return;
    const text = el.textContent.trim();
    if (!text) return;
    el.dataset.wordsDone = "1";

    if (prefersReducedMotion() || !hasGsap()) return;   // leave the text as-is

    el.innerHTML = text.split(/\s+/)
      .map((w) => '<span class="wr"><i>' + esc(w) + "</i></span>")
      .join(" ");

    window.gsap.registerPlugin(window.ScrollTrigger);
    window.gsap.from(el.querySelectorAll(".wr i"), {
      yPercent: 118,
      duration: 0.7,
      ease: "power3.out",
      stagger: 0.045,
      scrollTrigger: { trigger: el, start: "top 86%", once: true },
    });
  }

  /** Thin progress rail for the whole document. */
  function initScrollProgress() {
    const bar = document.getElementById("crProgress");
    if (!bar) return;
    function paint() {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? h.scrollTop / max : 0).toFixed(4) + ")";
    }
    document.addEventListener("scroll", paint, { passive: true });
    window.addEventListener("resize", paint);
    paint();
  }

  /* ------------------------------------------------------------------------
     Hero atmosphere. One effect only (the motion contract retired the particle field):

       typewriter — the headline cycles the thing being exploited. The words are
                    this product's real attack surfaces, so the motion carries
                    information instead of decorating the page.

     It may not run under prefers-reduced-motion: the headline renders one
     word statically.
     ------------------------------------------------------------------------ */
  function initTypewriter(el, words, opts) {
    if (!el || !words || !words.length) return;
    if (prefersReducedMotion()) { el.textContent = words[0]; return; }

    const o = opts || {};
    const typeMs = o.typeMs || 55;
    const eraseMs = o.eraseMs || 30;
    const holdMs = o.holdMs || 1900;
    // Never erase to nothing. An empty word leaves the headline reading
    // "Exploit ." with a gap before the full stop, which reads as a broken
    // render rather than an animation. Words share a prefix, so the floor
    // keeps that prefix on screen and only the noun cycles.
    const floor = Math.max(0, Math.min(o.minChars == null ? 0 : o.minChars, words[0].length));

    let wi = 0, ci = words[0].length, erasing = false;
    el.textContent = words[0];

    function tick() {
      const word = words[wi];
      if (!erasing) {
        if (ci < word.length) {
          ci++;
          el.textContent = word.slice(0, ci);
          setTimeout(tick, typeMs);
        } else {
          erasing = true;
          setTimeout(tick, holdMs);
        }
      } else {
        if (ci > floor) {
          ci--;
          el.textContent = word.slice(0, ci);
          setTimeout(tick, eraseMs);
        } else {
          erasing = false;
          wi = (wi + 1) % words.length;
          setTimeout(tick, typeMs);
        }
      }
    }
    setTimeout(tick, holdMs);
  }

  /** Just the id from a tag: "LLM03:2026 Excessive Agency" -> "LLM03". */
  function owaspId(tag) {
    const m = String(tag || "").match(/^(LLM[0-9]{2}|ASI[0-9]{2})/);
    return m ? m[1] : owaspLabel(tag);
  }

  /* ------------------------------------------------------------------------
     Areas designed but not authored. One array, read by catalog.html and
     roadmap.html -- never copied into a page, so the two can't disagree.
     `docs/CURRICULUM.md` is the prose version of this same list.
     ------------------------------------------------------------------------ */
  const ROADMAP = [
    { code:"WEB", title:"Web Application Security",   note:"OWASP Top 10 against a deliberately vulnerable app", certs:"PortSwigger WSA · BSCP · eWPT", role:"AppSec engineer / web pentester" },
    { code:"OFF", title:"Offensive Security",          note:"recon to root — the full kill chain on a target box", certs:"eJPT · PNPT · OSCP-prep", role:"Pentester, red teamer" },
    { code:"CLD", title:"Cloud Security",              note:"IAM misconfiguration and container hardening", certs:"AWS Security · CKS-adjacent", role:"Cloud security engineer" },
    { code:"DEV", title:"DevSecOps & Supply Chain",    note:"CI/CD security, secrets, SBOM, IaC scanning", certs:"vendor-neutral", role:"DevSecOps engineer" },
    { code:"DFR", title:"Digital Forensics & IR",      note:"memory and disk triage, incident playbooks", certs:"GCFA · GCIH-prep", role:"IR / forensics analyst" },
    { code:"RE",  title:"Malware Analysis & RE",       note:"static and dynamic analysis, no egress", certs:"GREM-prep", role:"Malware analyst" },
    { code:"NET", title:"Network & Fundamentals",      note:"packet analysis and protocols — the on-ramp", certs:"Security+ · Network+", role:"Entry-level analyst" },
    { code:"CRY", title:"Cryptography & Secrets",      note:"applied crypto, PKI, key-management failures", certs:"vendor-neutral", role:"AppSec / platform" },
    { code:"GRC", title:"Governance & Policy-as-Code", note:"OPA/Rego, NIST/ISO mapping, usable audit trails", certs:"vendor-neutral", role:"GRC analyst" },
  ];

  /** Roadmap entries for Areas that do not exist in /catalog yet. */
  function roadmapGaps(areas) {
    const built = new Set((areas || []).map((a) => (a.title || "").trim().toLowerCase()));
    return ROADMAP.filter((r) => !built.has(r.title.trim().toLowerCase()));
  }

  /** Chips carry "LLM03:2026 Excessive Agency" so the source stays auditable.
      The scheme is stated once per page, so strip the year at render time. */
  function owaspLabel(tag) {
    return String(tag || "").replace(/:[0-9]{4}(?![0-9])/, "");
  }

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

  /* ---- scroll reveal -------------------------------------------------------
     Auto-inits on DOMContentLoaded: observe every [data-reveal], add "is-in"
     on entry, unobserve. This is the one piece of motion that can blank the
     site if it breaks, so the rule is absolute: any failure mode here must be
     "no animation", never "no content". Reduced motion, a missing
     IntersectionObserver, or literally anything throwing all resolve the same
     way — reveal everything immediately. See docs/research/MOTION-NAV-CONTRACT.md. */
  function prefersReducedMotion() {
    try {
      return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch { return false; }
  }

  /** Last-resort: make every [data-reveal] under `root` visible, no animation. */
  function revealAllNow(root) {
    try {
      (root || document).querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-in"));
    } catch { /* if querySelectorAll itself is broken there is nothing left to try */ }
  }

  let revealObserver; // one shared observer; created lazily, reused across scans

  /** Find [data-reveal] elements under `root` (default: whole document) that
      haven't already fired and arrange for them to get "is-in". Safe to call
      repeatedly — already-revealed elements are skipped. Exposed as
      CR.revealScan(root) so pages can call it after they render fetched
      content; cyberrange.js also calls it itself on load and once more after
      a short delay to catch late renders. */
  function revealScan(root) {
    try {
      const scope = root || document;
      const targets = scope.querySelectorAll("[data-reveal]:not(.is-in)");
      if (!targets.length) return;

      if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
        targets.forEach((el) => el.classList.add("is-in"));
        return;
      }

      if (!revealObserver) {
        revealObserver = new IntersectionObserver((entries, obs) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-in");
              obs.unobserve(entry.target);
            }
          });
        }, { threshold: 0.1 });
      }
      targets.forEach((el) => revealObserver.observe(el));

      // Watchdog. IntersectionObserver can exist and still never fire — a
      // throttled background tab is the common case, an interfering extension
      // the other. That is indistinguishable from "broken" to a reader looking
      // at a blank page, and the try/catch above cannot see it because nothing
      // throws. So: if an element that is plainly inside the viewport has still
      // not been revealed shortly after we started observing, stop trusting the
      // observer and show everything. Degrades to no animation, never no content.
      setTimeout(() => {
        try {
          const stuck = [...scope.querySelectorAll("[data-reveal]:not(.is-in)")];
          const anyOnScreen = stuck.some((el) => {
            const r = el.getBoundingClientRect();
            return r.height > 0 && r.top < window.innerHeight && r.bottom > 0;
          });
          if (anyOnScreen) revealAllNow(scope);
        } catch { revealAllNow(scope); }
      }, 1200);
    } catch {
      // Whatever just broke, the content must not end up stuck invisible.
      revealAllNow(root);
    }
  }

  /* ---- mobile nav toggle -----------------------------------------------
     Any .cr-burger toggles .is-open on its closest .cr-nav. No-op on pages
     with no .cr-burger (scenario.html has its own player rail by design and
     carries no site nav). */
  function initNav() {
    document.querySelectorAll(".cr-burger").forEach((btn) => {
      if (btn.dataset.crNavBound) return;
      const nav = btn.closest(".cr-nav");
      if (!nav) return;
      btn.dataset.crNavBound = "1";

      const setOpen = (open) => {
        nav.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", String(open));
      };

      btn.addEventListener("click", () => setOpen(!nav.classList.contains("is-open")));
      nav.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && nav.classList.contains("is-open")) {
          setOpen(false);
          btn.focus();
        }
      });
      nav.querySelectorAll(".cr-links a").forEach((a) =>
        a.addEventListener("click", () => setOpen(false)));
    });
  }

  function boot() {
    try { initScrollProgress(); } catch (e) { /* enhancement */ }
    try { initTheme(); } catch (e) { /* theme is an enhancement */ }
    try { initAnnounce(); } catch { /* the strip is an enhancement, never a blocker */ }
    try { initSearch(); } catch (e) { /* search is an enhancement, never a blocker */ }
    try { initNav(); } catch { /* nav is an embellishment, never fatal */ }
    try { revealScan(document); } catch { revealAllNow(document); }

    // Every page here renders its real content from a fetch() that resolves
    // well after DOMContentLoaded, so a reveal target usually does not exist
    // yet at this point. A fixed timeout is a race against network latency and
    // loses on a slow response — the content then sits at opacity 0 forever
    // because nothing ever scans it. Watch the DOM instead and scan whenever
    // nodes actually land.
    try {
      if (typeof MutationObserver !== "undefined") {
        const mo = new MutationObserver((records) => {
          const added = records.some((r) => r.addedNodes && r.addedNodes.length);
          if (added) revealScan(document);
        });
        mo.observe(document.body, { childList: true, subtree: true });
      } else {
        revealAllNow(document);
      }
    } catch { revealAllNow(document); }

    // Belt and braces: whatever happened above, nothing stays invisible for
    // longer than this.
    setTimeout(() => {
      try { revealScan(document); } catch { revealAllNow(document); }
    }, 800);
  }
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
    else boot();
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

  return { STAGES, STAGE_LABEL, ROADMAP, roadmapGaps, owaspLabel, owaspId,
           initTypewriter, initSearch, openSearch, initAnnounce,
           initTheme, setTheme, activeTheme,
           hasGsap, initSmoothScroll, renderHops, initHopScrub, initWordReveal,
           esc, api, loadProgress, saveProgress, recordPass, isPassed,
           transcript, traceHTML, paintTrace, enhanceCode, revealScan };
})();
