People often ask whether a leaked system prompt actually matters. In this lab you
can answer that concretely — because the planner prompt documents:

- every tool name the agent can call,
- the exact argument shape for each one, and
- a worked `filter: "1=1"` **dump-all example**.

That's not an embarrassing disclosure. It's the exploit recipe for Module 1,
printed for the attacker.

You'll make the agent recite its instructions, detect the disclosure on the way
out, and then confront the uncomfortable part: detection is damage control. The
actual control is not putting anything in a system prompt you wouldn't publish.
