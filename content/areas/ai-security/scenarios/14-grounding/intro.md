Misinformation is the OWASP category people most often fake a defense for. So this
scenario starts by being precise about what it does.

You **cannot** deterministically check whether a statement is true about the
world. You **can** check whether a claim is **supported by the sources the answer
was built from** — and that is what production RAG systems actually deploy.

The failure you'll fix: the agent answers a shipping question correctly, then
adds *"we guarantee a lifetime money-back warranty"* — stated in exactly the same
confident voice, supported by nothing. Users act on that. Support desks get
held to it.
