## Direct vs indirect

| | Direct | Indirect (next labs) |
|--|--------|----------------------|
| Channel | User prompt | Retrieved doc, email, web page, memory |
| Who types the instruction | The attacker, in chat | Someone else's content the agent *reads* |
| Typical opener | "Ignore previous instructions…" | Hidden `SYSTEM NOTE` in a FAQ |
| Same payload? | Yes — `db_tool` + `filter=1=1` | Yes |

The model cannot reliably tell instructions from data. So the **executor** must
treat every plan as untrusted, including one that came from a "normal" user.

Encoding tricks, DAN personas, and multi-turn Crescendo attacks are the same
class. They are optional later. Core only needs you to see: **chat box → plan →
tool**.
