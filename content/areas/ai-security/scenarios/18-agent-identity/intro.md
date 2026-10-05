> **In plain terms.** A valet key lets the valet drive your car but not open the boot or the glovebox. The key sets the limit, not the valet's request. Here, the signed-in session decides whose records the agent may read, whatever the model asks for.
>
> *Where the analogy breaks:* a valet key is a physical object. A session is data, so it has to be bound on the server, where the model cannot touch it.

Parameterized SQL (the SQLi lab) stops `1=1` as a string. It does not decide
**whose** row is allowed.

OWASP calls this ASI03 Identity and Privilege Abuse: the
agent holds a powerful credential and an attacker (or a hijacked plan) spends it
on the wrong principal. In web AppSec this is the confused deputy. In agents it
is the default architecture — the tool server authenticates the **agent**, not
Alice.

This lab makes that explicit.
