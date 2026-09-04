## Write the timeline

Fill in the five questions from evidence. A defensible version reads roughly:

> Between `<first event>` and `<last event>`, three customer records — name,
> email and address — were read from the `customers` table via an unscoped query
> (`WHERE 1=1`) and delivered by the email tool to
> `audit@external-logging.test`, a destination outside our control. The path was
> a single agent run chaining two capabilities: database read, then outbound
> mail. No control interrupted either step. Activity is not ongoing; the run
> terminated.

Notice what that paragraph does **not** claim. It does not name a user, because
no source records one. It does not say the data left the building, because the
sink is local and nothing independently observed the network.

Say what the evidence supports, and mark the rest unknown. An investigation that
overstates gets unwound the moment somebody checks it — and then nobody believes
the parts that were right.
