# Contributing

Thanks for helping. CyberRange teaches AI-agent security by letting people break
a real agent and then prove a control stops it. Contributions should keep that
loop honest.

## Ground rules

- **Synthetic only.** Fake people, fake credentials, reserved domains
  (`.example`, `.test`). No real targets, ever.
- **No fabricated numbers on screen.** Every count, time or score in the UI is
  derived from content or lab state.
- **Run does the work, Check reads what it left behind.** Never write UI or copy
  that says Check runs anything. `tests/test_run_check_split.py` guards this.
- **Colour is never the only signal.** Every state carries a glyph, a word and a hue.
- **No literal colours** outside token declarations (`tests/test_ui_theme.py`).

## Adding a scenario

Copy the structure described in [content/AREA_TEMPLATE.md](content/AREA_TEMPLATE.md).
Each graded step needs a `checks/step-NN.json` with 1–4 `asserts`, an OWASP 2026
mapping (`LLMxx:2026` or `ASIxx`), and a secure-mode control that actually blocks it.

## Before you open a pull request

```text
docker compose up -d
python -m pytest tests/ -q
```

`tests/test_smoke.py::test_agent_end_to_end_with_tool_call` depends on a live
local model and can time out. Everything else must pass.

For UI changes, check the page at 390 px and 1280 px, in light and dark, with
the keyboard only.

## Licence

By contributing you agree that your contribution is licensed under the
[Apache License 2.0](LICENSE).
