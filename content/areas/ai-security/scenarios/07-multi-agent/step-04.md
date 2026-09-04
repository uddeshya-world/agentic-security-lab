## Prove tampering is caught

Run the same attack in secure mode. The plan is signed; when the
man-in-the-middle rewrites the recipient, the executor's verification fails and
the message is rejected. The rogue `shell_tool` is refused by the allow-list.

The **Check** confirms both: the tampered message is not executed and the rogue
tool is blocked.

Same attack, same intent — but now every hand-off is authenticated, so the extra
agents add capability without adding an unguarded trust boundary.
