## Three kinds of access

On any diagram of an AI agent, mark three things:

- **Untrusted content**: anything the public can write. Help-page edits, emails,
  remarks fields, chat messages, and the descriptions of third-party tools.
- **Private data**: records about people.
- **External communication**: email, web requests, file uploads, partner feeds.

A path that touches all three can leak. A path missing one of them cannot.
