## Read the payload

Look at the poison fixture shipped with the lab:

```bash
cat data/corpus/poisoned/doc_evil_001.txt
```

Notice its shape: it looks like a normal knowledge-base note about shipping or
policy, but it embeds an instruction block aimed at the *assistant*, telling it
to dump customers and email them to an external address.

It is tagged with metadata `trust=untrusted` when ingested — that tag is what
the defense will later key on. In the real world you would have to infer trust
from the source; here it is explicit so the lesson stays clean.
