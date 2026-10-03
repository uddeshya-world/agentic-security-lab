Parameterized SQL (the SQLi lab) stops `1=1` as a string. It does not decide
**whose** row is allowed.

OWASP calls this ASI03 Identity and Privilege Abuse: the
agent holds a powerful credential and an attacker (or a hijacked plan) spends it
on the wrong principal. In web AppSec this is the confused deputy. In agents it
is the default architecture — the tool server authenticates the **agent**, not
Alice.

This lab makes that explicit.
