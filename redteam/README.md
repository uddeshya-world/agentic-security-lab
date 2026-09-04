# Red-team harness

**v1.0 status: wiring / smoke only — not a full red-team suite.**  
Module 1 measurement uses `attacks/m01` + `metrics/m01`, not these tools.

Pre-wired for DeepTeam, Promptfoo, and Garak against the local agent's HTTP
endpoint (`http://127.0.0.1:8000/run`), not just the bare LLM. Each probe is
trivial by design (prove wiring, not coverage).

| Tool | Entry point | Integration shape | Verified vs assumed |
|---|---|---|---|
| DeepTeam | `deepteam/run_deepteam_probe.py` | `model_callback` wrapping the agent HTTP endpoint | Falls back to a plain HTTP probe if `deepteam`'s `red_team`/`Bias` API differs from what was assumed at plan time -- check console output for which path ran. |
| Promptfoo | `promptfoo/promptfooconfig.yaml` | `http` provider, `transformResponse` pulls `final_answer` | Verify `transformResponse` JS-expression syntax against the installed promptfoo version. |
| Garak | `garak/run_garak_probe.py` | `garak.generators.rest.RestGenerator` pointed at the agent endpoint | Falls back to a plain HTTP probe if `RestGenerator`'s config shape differs from what was assumed at plan time. |

Run order: bring up the full stack (`./run.sh up && ./run.sh wait`), then:

    python redteam/deepteam/run_deepteam_probe.py
    npx promptfoo eval -c redteam/promptfoo/promptfooconfig.yaml
    python redteam/garak/run_garak_probe.py

Real attack-dataset coverage mapped to OWASP Agentic (ASI) categories is out
of scope for modules 0/1 -- see PROMPT 6 (Red-Teaming & Evaluation Framework)
in the prompt pack.
