# Motion + nav contract — pass 2

> Measured from escbash.com on 2026-09-08. Their whole homepage runs **two** CSS animations
> (a 1.1s `steps(1)` cursor blink and a 28s marquee); the starfield is a `<canvas>` and the demo is a
> `<video>`. The polish comes from **transitions**, not animations: ~30 elements at
> `opacity, transform @ 0.55s` (scroll reveal) and ~10 at `@ 0.15s` (hover/press). Two speeds,
> applied everywhere. `prefers-reduced-motion` is honored.
>
> CyberRange has **6 transitions total across four pages** and no scroll reveals. That gap — not the
> absence of ambient decoration — is why the product reads unfinished.
>
> **Decided:** no starfield, no typewriter headline, no marquee. The hero keeps the breach animation
> as the single signature moment. Build the motion system and the nav instead.

---

## File ownership

Cross-cutting work, so the contract below is pinned first and each agent owns disjoint files.

| Agent | Owns | Never touches |
|---|---|---|
| **A — foundation** | `lab/ui/cyberrange.css` | every `.html`, `cyberrange.js` |
| **B — site pages** | `catalog.html`, `area.html`, `index.html`, `verify.html` | `cyberrange.css`, `cyberrange.js`, `scenario.html` |
| **C — player + behaviour** | `scenario.html`, `cyberrange.js` | `cyberrange.css`, the four site pages |

The `:root` token freeze from pass 1 is **lifted for Agent A only**. A may add the motion tokens
below and nothing else. B and C still may not touch tokens.

---

## 1. Motion tokens — Agent A adds to `:root`

```css
--t-fast: 150ms;   /* interaction: hover, press, focus */
--t-slow: 550ms;   /* entrance: scroll reveal */
--ease:   cubic-bezier(0.22, 0.61, 0.36, 1);
```

Two speeds. Nothing else. If a third duration seems necessary, it is a sign the effect is
decoration — drop the effect instead of adding the token.

## 2. Scroll reveal

**A provides the CSS. C provides the auto-init JS. B and C only add the attribute.**

```html
<section data-reveal>…</section>
<div data-reveal data-reveal-delay="1">…</div>   <!-- stagger: 1|2|3 -->
```

```css
[data-reveal] { opacity: 0; transform: translateY(12px);
                transition: opacity var(--t-slow) var(--ease),
                            transform var(--t-slow) var(--ease); }
[data-reveal].is-in { opacity: 1; transform: none; }
[data-reveal-delay="1"] { transition-delay:  60ms; }
[data-reveal-delay="2"] { transition-delay: 120ms; }
[data-reveal-delay="3"] { transition-delay: 180ms; }

@media (prefers-reduced-motion: reduce) {
  [data-reveal] { opacity: 1; transform: none; transition: none; }
}
```

`cyberrange.js` auto-inits on DOMContentLoaded: observe every `[data-reveal]` with an
IntersectionObserver, add `.is-in` on entry, unobserve. **If `prefers-reduced-motion` is set, or
IntersectionObserver is unavailable, add `.is-in` to everything immediately** — content must never
be stuck invisible.

## 3. Interaction states

A adds `transition: … var(--t-fast) var(--ease)` to the existing `.btn`, `.tag`, `a.link`,
`.card`/tile, and `.slate tbody tr` rules, plus:

- `.lift:hover { transform: translateY(-2px); }`
- a `:active` press state on `.btn` (settle to `translateY(0)`)
- `:focus-visible` must stay visible and must not be a transition-only affordance

## 4. Nav

A builds the CSS. B puts this markup on all four site pages. `scenario.html` keeps its player rail
and gets **no site nav** — that separation is deliberate.

```html
<header class="cr-nav">
  <a class="cr-mark" href="/lab/ui/catalog.html"><span class="glyph"></span>CyberRange</a>
  <nav class="cr-links" id="crlinks">
    <a class="link is-active" href="/lab/ui/catalog.html">Range</a>
    <a class="link" href="/lab/ui/index.html">Sandbox</a>
    <a class="link" href="/lab/ui/verify.html">Verify a badge</a>
  </nav>
  <span class="grow"></span>
  <button class="cr-burger" aria-label="Menu" aria-controls="crlinks" aria-expanded="false">☰</button>
</header>
```

- `is-active` is set **by hand, per page** — these are static pages and CSS cannot compare two
  attributes. Exactly one link per page carries it.
- **Mobile:** below 720px `.cr-links` becomes a panel toggled by `.cr-burger`, which is hidden above
  720px. C wires the toggle in `cyberrange.js`: any `.cr-burger` toggles `.cr-nav.is-open` and keeps
  `aria-expanded` in sync. Escape closes it; focus returns to the button.
- **Dot badge** `<span class="pip"></span>` — A styles it 6px, `border-radius:50%`, `--brass`.
  Use it **only where a real signal exists** (an Area whose status is `authoring`, say). There is no
  publish-date field in `catalog_payload()` today, so **do not add a "new" badge** — that would be
  the fabricated-data rule all over again.

## 5. Out of scope this pass

Search in the nav (23 scenarios do not need it), a theme toggle (light theme is its own pass), auth,
and anything from the ambient-FX list above.
