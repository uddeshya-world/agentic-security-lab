## Scan it, then run it again

Many skill registries run a scanner before listing a skill. The lab's scanner in
`defenses/m07/skill_manifest.py` looks for the usual patterns: `curl`, `wget`, `base64`,
`eval`, `exec`, `subprocess`, reverse shells, pipe-to-shell.

**Run** scans `SKILL.md` for real and then runs the skill, still in vulnerable mode.
**Check** reads the evidence: the scanner reported clean, and the export still went
out.

> **Caveat.** A scanner is not a stop. It looks for code, and this skill has none.
> That is AST08, poor scanning.
