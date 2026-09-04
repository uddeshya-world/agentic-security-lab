## What is not recorded

Name the blind spots before you rely on the evidence, not after.

- **No identity.** No row in the event log says which user or which session caused
  it. One learner and one attacker look identical.
- **Two different clocks.** The event log is cleared when a run starts. The mail
  sink is cleared by nobody.
- **No independent egress record.** The email tool reports what it sent. Nothing
  else watches the network, so a tool that lied would not be caught here.
- **No baseline.** You have no idea what a normal day looks like, because a lab
  has no normal days.

Every one of those is a real gap in real deployments. Write them down. In
scenario 2 you will build a detection, and a detection that assumes a field you
do not have is worse than no detection at all.
