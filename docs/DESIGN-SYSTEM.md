# CyberRange design system

One stylesheet, three tiers, enforced by a test. Everything visual in the product
comes from `lab/ui/cyberrange.css`; pages add only what is theirs alone.

The system predates this document — the ember/halon palette, the motion rules and
the player components were already there. What was added is the **scale tier**
(type, radius, elevation, layout) and the **semantic alias tier** that sits
between components and the raw palette, so a surface can be re-pointed in one
place instead of thirty.

---

## 1. The idea the visuals encode

The product measures one thing: **how far a compromised step travels before
something stops it.** So two temperatures carry all the meaning, and nothing else
in the palette is allowed to compete with them.

| Token | Means | Never used for |
|---|---|---|
| `--ember` | the attack propagating; a thing that succeeded when it should not have | emphasis, branding, "primary" |
| `--halon` | the control that contained it (halon is a fire-suppression agent) | success in the generic sense |
| `--brass` | a caveat — pending, partial, or "read this before you trust it" | warnings about the UI itself |

Chrome is greyscale on a cool charcoal ground precisely so those three are the
only saturated things on screen, and so they always mean the same thing.

**A colour on this product is a claim about what happened.** Do not reach for
ember because a heading needs energy.

---

## 2. Tiers

### Tier 1 — raw palette and scales

Ground (`--void` → `--edge-hi`), ink (`--chalk`/`--ash`/`--dim`), the three
temperatures, and the derived roles (`--sunk`, `--prose`, `--term-bg`, …).

Scales, all of which are closed sets — a value not on the ramp is a bug:

- **Space** `--s1`…`--s8` (4 · 8 · 12 · 16 · 24 · 32 · 48 · 72)
- **Radius** `--r-xs` · `--r-sm` · `--r` · `--r-lg` · `--r-xl` · `--r-full`
- **Type** `--fs-2xs` … `--fs-hero`, plus `--fw-*`, `--lh-*`, `--tr-*`
- **Elevation** `--sh-sm` · `--sh-md` · `--sh-lg`
- **Motion** `--t-fast` · `--t-slow` · `--ease` — two speeds, no third
- **Layout** `--content-max` · `--reading-max` · `--nav-h`

Radii are small on purpose. This is an instrument panel, not a consumer app.
`--r-xl` is reserved for the two surfaces that float above the grid (dialog,
toast), and those are also the only two that may use `--sh-lg`.

Each shadow is three stacked layers — a tight contact shadow, a soft spread, and
a hairline ring that does a 1px border's job without taking layout. Depth reads
as distance from the plate, which is why every layer is low-opacity.

### Tier 2 — semantic aliases

Components reference these, **never** tier 1:

```
--surface-page  --surface-card  --surface-raised  --surface-sunk  --glass-panel
--text-1  --text-2  --text-3
--line  --line-strong
--state-vuln  --state-secure  --state-pass  --state-fail  --state-pending
```

The state group is the pedagogy in token form. `--state-vuln` is the attack that
landed; `--state-secure` is the control that contained it. They alias ember and
halon today; naming them separately is what lets the palette move without
rewriting every component.

### Tier 3 — components

Shared components live in the *Catalogue & player components* section of
`cyberrange.css`. A component used by one page stays in that page's `<style>`;
the moment a second page needs it, it moves into the shared section.

---

## 3. Colour is never the only carrier

The product reports security outcomes. A learner who cannot separate ember from
halon must still be able to read whether the attack landed. So every stateful
component carries **three redundant signals**:

| Component | Glyph | Word | Hue |
|---|---|---|---|
| `.check.pass` | `✓` | PASS | halon |
| `.check.fail` | `✗` | NOT YET | ember |
| `.check.pending` | `·` | CHECKING | brass |
| `.modebanner.vulnerable` | — | VULNERABLE | ember |
| `.modebanner.secure` | — | SECURE | halon |
| `.steprail .is-done` | ringed index | state word | halon |

If you add a variant, add all three. A patch that introduces a colour-only state
should not pass review.

---

## 4. Theming

Light is not a separate stylesheet — it is a **redefinition of tokens only**.
Three blocks must agree:

1. `:root` — the dark values (the default)
2. `@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) }`
3. `:root[data-theme="light"]` — the explicit choice, which must beat the system

CSS cannot share a value list between two selectors, so 2 and 3 are duplicated
and `tests/test_ui_theme.py` is the only thing stopping them from drifting.

**Rules this enforces, and why each one bites:**

- Every colour-valued token in `:root` needs a light counterpart, or it will not
  switch.
- No literal colour may appear outside a token declaration — in
  `cyberrange.css` or in any `lab/ui/*.html`. A hex in a rule body survives the
  theme switch and turns into invisible text on the opposite ground.
- The test reads **line by line**, so a multi-line token value reads as a stray
  colour. Keep each declaration on one line.
- All pages must agree on the `?v=` asset version, so a returning browser never
  gets new markup against a cached stylesheet.

Run it: `python -m pytest tests/test_ui_theme.py -q`

---

## 5. Typefaces

All three are open-licensed and loaded from Google Fonts:

| Role | Family | Licence |
|---|---|---|
| `--display` | Space Grotesk | SIL Open Font License 1.1 |
| `--body` | Archivo | SIL Open Font License 1.1 |
| `--mono` | JetBrains Mono | SIL Open Font License 1.1 |

The signature move is **mono, uppercase, `--tr-caps` tracked** for every eyebrow,
kicker and metadata row. It labels a region without competing with the heading,
and it is most of why the product reads as an instrument rather than a course.

---

## 6. Assets

In `lab/ui/assets/`:

- **`mark.svg`** — the logo. Three ember pips travel left to right, each larger
  than the last; the halon bar is where the travel ends. It is the product's one
  sentence. Remove the bar and the mark means the opposite thing. Inherits
  `currentColor`, so it themes.
- **`favicon.svg`** — a two-pip variant for 16px, with literal colours, because
  the browser composites a favicon outside the page and it cannot inherit.
- **`texture-halftone.svg`** — a tileable 120px halftone for card headers and
  empty states. Opacity is applied by the consuming rule, not baked in, so one
  file serves both themes.

---

## 7. Adding to the system

1. Can an existing component do it? Use it.
2. Does it need a value off the ramp? The ramp is probably right and the design
   is probably wrong. Change the design.
3. New shared component → the *Catalogue & player components* section, built from
   tier 2 aliases only.
4. New colour token → all three theme blocks, one line each, then run the test.
5. New state → glyph, word, and hue. All three.
