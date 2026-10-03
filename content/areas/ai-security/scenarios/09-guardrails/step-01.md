## From seams to a real layer

Open `guardrails/pipeline.py`. It has two scanners, the same shape LLM Guard /
NeMo rules take:

```python
scan_input(text)   # catches prompt-injection / jailbreak shapes
scan_output(text)  # catches PII egress and secret leakage
```

And a benchmark harness:

```python
run_benchmark(probes)  # -> catch_rate, false_positive_rate, p50/p95 latency
```

The point isn't that these regex scanners are production-grade (a real deployment
layers a classifier and an LLM judge on top). The point is the **discipline**:
every guardrail is evaluated against a labeled set so you know its catch rate and
its false-positive cost before it goes in front of users.

`scan_input` is a **prompt-injection** detector. `scan_output` / `scan_data` are
**data guards** (PII, secrets). Content-safety classifiers (hate, sexual, denied
topics) are a third family — Llama Guard, Azure harm categories. Do not report
them as one number. The Core DLP lab is C21; this lab is how you *measure* it.
