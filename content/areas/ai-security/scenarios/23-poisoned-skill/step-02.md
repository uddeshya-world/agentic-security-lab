## Run the skill

**Run** loads the skill in vulnerable mode, where the runtime ignores the manifest and
the skill acts with the agent's own privileges. **Check** reads what the run left
behind.

Expect the timeline to show the planner following the usage notes, the file tool
reading the export, and MailHog holding a message to `reports@ward-data.example`.
Nothing left this machine: MailHog is the sink, and every row is synthetic.
