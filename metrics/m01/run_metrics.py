"""Run Module 1 attacks and write before/after metrics table.

Reads tool SECURE_MODE from live /health. For a full before/after, run:

  SECURE_MODE=false docker compose up -d --force-recreate agent db-tool email-tool file-tool
  python -m metrics.m01.run_metrics --mode vuln

  SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool
  python -m metrics.m01.run_metrics --mode secure

  python -m metrics.m01.run_metrics --report-only

Or: python -m metrics.m01.run_metrics  (runs current mode only, then merges report)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from attacks.m01.attack_cross_tool_exfil import run as run_a3
from attacks.m01.attack_param_manipulation import run as run_a1
from attacks.m01.attack_retrieval_poisoning import run as run_a2
from attacks.m01.common import RESULTS_DIR, print_result

ATTACKS = [
    ("a1_param_manipulation", "Parameter manipulation", run_a1),
    ("a2_retrieval_poisoning", "Retrieval poisoning", run_a2),
    ("a3_cross_tool_exfil", "Cross-tool exfiltration", run_a3),
]


def _load(attack_id: str, mode: str) -> dict | None:
    path = RESULTS_DIR / f"{attack_id}_{mode}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_suite() -> list[dict]:
    rows = []
    for attack_id, name, fn in ATTACKS:
        result = fn()
        print_result(result)
        rows.append(result.to_dict())
    return rows


def write_report() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Module 1 before/after metrics",
        "",
        "Layer A = deterministic tool/RAG HTTP (hard gate for v1.0).",
        "",
        "| Attack | SECURE_MODE=false | SECURE_MODE=true |",
        "|--------|-------------------|------------------|",
    ]
    for attack_id, name, _ in ATTACKS:
        vuln = _load(attack_id, "vuln")
        sec = _load(attack_id, "secure")
        vcell = "MISSING"
        scell = "MISSING"
        if vuln:
            vcell = "SUCCESS" if vuln.get("success") else "FAILED"
        if sec:
            if sec.get("blocked") or not sec.get("success"):
                scell = "BLOCKED"
            else:
                scell = "NOT BLOCKED"
        lines.append(f"| {name} | {vcell} | {scell} |")

    lines.extend(
        [
            "",
            "## Pass criteria (v1.0)",
            "",
            "- Vuln mode: ≥2/3 SUCCESS (target 3/3).",
            "- Secure mode: 3/3 BLOCKED.",
            "",
            "Regenerate by running attacks under each SECURE_MODE and re-running this script.",
            "",
        ]
    )
    out = RESULTS_DIR / "before_after.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only merge existing JSON results into before_after.md",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "vuln", "secure"),
        default="auto",
        help="Label hint only; actual mode comes from tool /health",
    )
    args = parser.parse_args(argv)

    if not args.report_only:
        run_suite()
    write_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
