## The real fix is upstream

Run the attack in secure mode. The **Check** confirms the leak is caught and the
response withheld.

Now the honest caveat, because this is where a lot of teams fool themselves:

**A leak detector is damage control, not a boundary.** A determined attacker can
paraphrase, translate, base64, or split the disclosure across turns. Detection
raises the cost; it doesn't make the prompt confidential.

So treat the system prompt as **public by design**:

- No credentials, keys, or internal URLs in it — ever.
- No security policy that only works while it stays hidden. Policy belongs in the
  executor and tool servers (controls C1–C7), where it holds even when the
  attacker knows exactly what it says.
- Assume the attacker has read your prompt, then ask whether your system is still
  safe. In this lab, after Modules 1–8, the answer is yes — that's the point.
