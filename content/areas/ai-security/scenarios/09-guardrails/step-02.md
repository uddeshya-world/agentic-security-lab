## Attacks with guardrails off

Run in vulnerable mode: the guardrail layer is disabled, so every malicious probe
passes unfiltered — prompt injections on the input side, PII and secret leakage
on the output side.

The **Check** confirms the baseline: with no guardrail, the attacks get through
(catch rate 0%). This is the "before" number in your effectiveness story.

You need this baseline. "We added guardrails" means nothing without the delta
against a run where they were off.
