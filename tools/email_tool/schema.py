def get_schema() -> dict:
    """Vulnerable mode: no allow-list on recipient domain, no size/rate limit --
    this is what lets cross-tool exfiltration and retrieval-triggered
    unprompted sends work (see attacks/01)."""
    return {
        "name": "email_tool",
        "description": "Send an email via the local mail sink.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    }
