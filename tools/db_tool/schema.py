def get_schema() -> dict:
    """Deliberately loose schema -- accepts a raw filter fragment in vulnerable
    mode (SECURE_MODE=false). This is the injection surface attacks/01 targets.
    In SECURE_MODE=true, defenses/01/least_privilege.py enforces a parameterized
    customer_id scope instead, but this declared schema stays the same on
    purpose -- the defense changes behavior, not the advertised contract,
    matching how a real permissive-schema tool would look from the outside.
    """
    return {
        "name": "db_tool",
        "description": "Query synthetic customers/orders data.",
        "parameters": {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "customers or orders"},
                "filter": {
                    "type": "string",
                    "description": "Raw SQL WHERE-clause fragment, e.g. \"customer_id = 1\"",
                },
            },
            "required": ["table", "filter"],
        },
    }
