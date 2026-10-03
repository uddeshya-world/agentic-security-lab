"""Guard the UI's theming contract.

The light palette has to exist in two CSS blocks -- one for the system
preference, one for an explicit choice that must beat it -- and CSS has no way
to share a value list between two selectors. So the two are duplicated, and the
only thing stopping them from drifting is this test.

The second guard is the one that actually breaks pages: a literal colour in a
page or in the shared stylesheet outside the token block does not change with
the theme, so it survives the switch and turns into invisible text on the
opposite ground.
"""
from __future__ import annotations

import re
from pathlib import Path

UI = Path(__file__).resolve().parents[1] / "lab" / "ui"
CSS = UI / "cyberrange.css"

# A literal colour is not only a hex. The nav bar shipped a hardcoded
# rgba(10, 12, 16, .92) that a hex-only scan walked straight past, which left the
# header dark on a light page -- so match the functional notations too.
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")



def _in_comment(css: str, lineno: int) -> bool:
    """True when the 1-indexed line sits inside a /* ... */ block."""
    upto = chr(10).join(css.splitlines()[:lineno])
    return upto.count("/*") > upto.count("*/")


def _decls(block: str) -> dict[str, str]:
    out = {}
    for line in block.splitlines():
        m = re.match(r"\s*(--[a-z0-9-]+)\s*:\s*([^;]+);", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def _block_after(text: str, marker: str) -> str:
    i = text.index(marker)
    depth, start, j = 0, None, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
            if start is None:
                start = j
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start:j]
        j += 1
    raise AssertionError(f"unbalanced block after {marker!r}")


def test_light_palette_blocks_do_not_drift():
    css = CSS.read_text(encoding="utf-8")
    media = _decls(_block_after(css, ':root:not([data-theme="dark"]) {'))
    explicit = _decls(_block_after(css, ':root[data-theme="light"] {'))
    assert media, "system-preference light block has no declarations"
    assert media == explicit, (
        "the two light-theme blocks have drifted:\n"
        + "\n".join(
            f"  {k}: media={media.get(k)!r} explicit={explicit.get(k)!r}"
            for k in sorted(set(media) | set(explicit))
            if media.get(k) != explicit.get(k)
        )
    )


def test_every_dark_token_has_a_light_value():
    css = CSS.read_text(encoding="utf-8")
    dark = _decls(_block_after(css, ":root {"))
    light = _decls(_block_after(css, ':root[data-theme="light"] {'))
    # Only colour-ish tokens need a light counterpart; spacing and timing do not.
    colourish = {
        k: v for k, v in dark.items()
        if HEX.match(v.strip())
    }
    missing = sorted(set(colourish) - set(light))
    assert not missing, f"tokens with no light value (they will not switch): {missing}"


def test_no_literal_colours_outside_the_token_blocks():
    """A hex in a rule body ignores the theme and survives the switch."""
    offenders = []

    css = CSS.read_text(encoding="utf-8")
    for n, line in enumerate(css.splitlines(), 1):
        if not HEX.search(line):
            continue
        if re.match(r"\s*--[a-z0-9-]+\s*:", line):   # a token definition
            continue
        if _in_comment(css, n):                      # prose explaining the palette
            continue
        # A mask stop is an alpha channel, not a colour: #000 there means
        # "fully opaque here", and it is correct in both themes.
        if "mask-image" in line and "#000" in line:
            continue
        offenders.append(f"cyberrange.css:{n}: {line.strip()[:80]}")

    for page in sorted(UI.glob("*.html")):
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            if not HEX.search(line):
                continue
            if re.match(r"\s*--[a-z0-9-]+\s*:", line):
                continue
            if "&#" in line or "href=" in line:
                continue
            if "mask-image" in line and "#000" in line:
                continue
            offenders.append(f"{page.name}:{n}: {line.strip()[:80]}")

    assert not offenders, "literal colours will not follow the theme:\n" + "\n".join(offenders)


def test_every_site_page_carries_the_full_nav():
    """One nav, five links, exactly one marked current."""
    expected = ["Range", "Roadmap", "Certifications", "Sandbox", "Verify a badge"]
    for name in ("catalog.html", "area.html", "index.html", "verify.html",
                 "roadmap.html", "certifications.html"):
        s = (UI / name).read_text(encoding="utf-8")
        nav = re.search(r'<nav class="cr-links".*?</nav>', s, re.S)
        assert nav, f"{name} has no nav block"
        labels = re.findall(r'<a class="link(?: is-active)?" href="[^"]+">([^<]+)</a>', nav.group(0))
        assert labels == expected, f"{name} nav is {labels}"
        assert nav.group(0).count("link is-active") == 1,             f"{name} must mark exactly one link current"
        assert "cr-search-btn" in s, f"{name} has no search trigger"
        assert "cr-theme" in s, f"{name} has no theme toggle"

    # The player deliberately has no site nav -- it keeps its own step rail.
    player = (UI / "scenario.html").read_text(encoding="utf-8")
    assert "cr-nav" not in player, "scenario.html must not carry the site nav"


def test_asset_version_is_uniform():
    """A returning browser must not get new markup against cached assets."""
    versions = set()
    for page in sorted(UI.glob("*.html")):
        versions.update(re.findall(r"cyberrange\.(?:css|js)\?v=(\d+)", page.read_text(encoding="utf-8")))
    assert len(versions) == 1, f"pages disagree on the asset version: {sorted(versions)}"


def test_vendored_libraries_are_present_and_pinned():
    """The scroll layer is vendored so the lab keeps working offline."""
    vendor = UI / "vendor"
    expected = {"gsap.min.js", "ScrollTrigger.min.js", "lenis.min.js"}
    present = {p.name for p in vendor.glob("*.js")}
    assert expected <= present, f"missing vendored libraries: {sorted(expected - present)}"
    for name in expected:
        assert (vendor / name).stat().st_size > 5000, f"{name} looks truncated"
    readme = (vendor / "README.md").read_text(encoding="utf-8")
    for name in expected:
        assert name in readme, f"{name} has no provenance entry in vendor/README.md"


def test_no_page_loads_the_scroll_libraries_from_a_cdn():
    """The footer promises no external targets; a hotlink would make that false."""
    offenders = []
    for page in sorted(UI.glob("*.html")):
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            if "<script" not in line:
                continue
            if re.search(r'src="https?://', line):
                offenders.append(f"{page.name}:{n}: {line.strip()[:90]}")
    assert not offenders, "scripts loaded from a remote origin:\n" + "\n".join(offenders)


def test_scroll_layer_degrades_without_the_vendor_directory():
    """Every scroll-narrative entry point must guard on the library being there.

    vendor/README.md promises the pages still render and every graded check still
    works with the directory absent. That promise is only true while these guards
    exist, so it is asserted rather than trusted.
    """
    js = (UI / "cyberrange.js").read_text(encoding="utf-8")
    guarded = {
        "initSmoothScroll": "!window.Lenis",
        "initHopScrub": "!hasGsap()",
        "initWordReveal": "!hasGsap()",
    }
    for fn, guard in guarded.items():
        m = re.search(r"function " + fn + r"\(.*?\n  \}", js, re.S)
        assert m, f"{fn} not found"
        assert guard in m.group(0), f"{fn} does not guard on {guard}"

    # The reveal system that pages fall back to must not depend on the libraries.
    m = re.search(r"function revealScan\(.*?\n  \}", js, re.S)
    assert m and "gsap" not in m.group(0).lower(), "revealScan must not depend on GSAP"
