# Vendored front-end libraries

These are committed rather than loaded from a CDN on purpose. The lab's own
footer says **"Local only · no external targets"**, and people run this
air-gapped or on a disconnected training machine. A page that silently reaches
out to `cdnjs` at load time would make that claim false.

Nothing here is modified. Re-fetch with the exact commands below to verify.

| File | Version | Source | Bytes |
|---|---|---|---|
| `gsap.min.js` | 3.12.5 | `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js` | 72214 |
| `ScrollTrigger.min.js` | 3.12.5 | `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js` | 43380 |
| `lenis.min.js` | 1.1.13 | `https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js` | 13485 |
| `marked.min.js` | 12.0.2 | `https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js` | 35479 |

```bash
curl -o gsap.min.js          https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
curl -o ScrollTrigger.min.js https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js
curl -o lenis.min.js         https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js
curl -o marked.min.js        https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js
```

## Licences

- **GSAP + ScrollTrigger** — GreenSock Standard License
  (<https://gsap.com/standard-license>). It covers use in a free, publicly
  accessible project like this one. It does **not** cover a product where
  multiple customers are charged for access. If CyberRange ever gains a paid
  tier, this dependency needs re-licensing (Club GSAP) or replacing — the
  scroll work is deliberately isolated in `cyberrange.js` so it can be swapped.
- **Lenis** — MIT (Studio Freight / darkroom.engineering).
- **marked** — MIT (Christopher Jeffrey).

## marked is not optional

`marked` is different from the other three. `scenario.html` renders every lesson
step through it, and that page was hotlinking it from `cdnjs` — so the core
player, the thing the whole product exists to deliver, could not render a lesson
on a disconnected machine. That is now served locally like everything else.
`tests/test_ui_theme.py` fails the build if any page reintroduces a remote
`<script src>`.

## What depends on them

**GSAP, ScrollTrigger and Lenis are optional.** They drive the scroll narrative
only. `cyberrange.js` feature-detects `window.gsap` / `window.Lenis` and falls
back to the IntersectionObserver reveal system, so deleting them degrades the
motion and nothing else: the hop diagram still renders complete and static,
every page still loads, every graded check still runs.
`tests/test_ui_theme.py::test_scroll_layer_degrades_without_the_vendor_directory`
asserts those guards are still in place.

**`marked` is required.** `scenario.html` renders lesson markdown through it,
so removing it breaks the player. It is not feature-detected because there is
no meaningful fallback — raw markdown is not a lesson.

## Still external: web fonts

Not everything is local yet. Every page pulls Space Grotesk, Archivo and
JetBrains Mono from `fonts.googleapis.com`. That degrades safely — each face
has a real fallback stack, so an offline machine gets system fonts and a
readable page — but it is still an outbound request, and self-hosting the three
families is the remaining work to make "no external targets" literally true.
