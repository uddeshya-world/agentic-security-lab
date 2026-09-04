## Four limits, one guard

Open `defenses/m11/limits.py`. `ResourceGuard` enforces four limits on every call
and raises `LimitExceeded` naming the control that fired:

```python
step-cap       plan exceeded max_steps
rate-limit     too many calls in the window
loop-detector  identical call repeated > max_repeats
cost-budget    session spend exhausted
```

Order matters. The **loop detector** keys on a signature of `(tool, args)`, so a
repeated identical call trips it long before the raw step count or the budget
would — catching the runaway at call 4 instead of call 8.

This is **control C20 — resource limits**. Together the four cover the gaps the
step cap left: shape (loops), spend (budget), speed (rate), and length (steps).
