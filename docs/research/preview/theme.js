/* Theme toggle for the AI Security Lab preview pages.
 *
 * Three states, not two: "light", "dark", and no stored choice at all — which
 * means follow the system, and the CSS handles that on its own. So this file
 * only ever stamps or clears a data-theme attribute; it never computes a
 * palette.
 *
 * The attribute is applied by a small inline snippet in each page's <head>,
 * before first paint, so navigating between pages does not flash the wrong
 * ground. This file is what wires the button afterwards.
 */
(function () {
  "use strict";

  var KEY = "aisl.theme";

  function stored() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : null;
    } catch (e) {
      return null; // private mode: the toggle still works, it just won't persist
    }
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function active() {
    return stored() || (systemPrefersDark() ? "dark" : "light");
  }

  function apply(mode) {
    document.documentElement.setAttribute("data-theme", mode);
    try { localStorage.setItem(KEY, mode); } catch (e) { /* not fatal */ }
    label();
  }

  var SUN =
    '<svg class="sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/>' +
    '<path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4' +
    'M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>';
  var MOON =
    '<svg class="moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function label() {
    var next = active() === "dark" ? "light" : "dark";
    Array.prototype.forEach.call(document.querySelectorAll(".theme-toggle"), function (b) {
      b.setAttribute("aria-label", "Switch to " + next + " theme");
      b.setAttribute("title", "Switch to " + next + " theme");
    });
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll(".theme-toggle"), function (btn) {
      if (!btn.querySelector("svg")) btn.innerHTML = SUN + MOON;
      btn.addEventListener("click", function () {
        apply(active() === "dark" ? "light" : "dark");
      });
    });
    label();

    // Someone who has never pressed the button is following the system, so the
    // page should keep following it when the system changes under them.
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var onChange = function () { if (!stored()) label(); };
      if (mq.addEventListener) mq.addEventListener("change", onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
