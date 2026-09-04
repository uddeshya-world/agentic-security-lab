## The obvious rule, and why it fails

The obvious rule after reading scenario 1 is *alert when the agent sends an
email*.

Work out what it costs. The email tool exists because the product needs it: order
confirmations, password resets, support replies. A rule on that event fires on
every legitimate use. Within a week it is muted, and the one firing that mattered
is muted with it.

That is not a tuning problem you fix later. A rule whose true-positive rate is
near zero is a rule that removes attention from wherever the attention was.

The useful question is never *what event happened*. It is **which field made this
run different from every ordinary one**.
