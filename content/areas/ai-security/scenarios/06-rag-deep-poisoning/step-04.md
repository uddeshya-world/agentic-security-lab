## Prove the context is clean

Run the same attack in secure mode. The timeline now shows both layers firing:
Module 1's trust filter drops the labeled crowding, and the Module 2 detector
quarantines the false-provenance chunk by its content.

The **Check** confirms the delivered context contains **zero** poison chunks and
still has at least one legitimate shipping chunk — the feature works, the attack
doesn't.

That's the whole lesson: **provenance labels are a hint, not a control.** The
enforceable control is content inspection plus crowding collapse, applied at the
moment context is assembled.
