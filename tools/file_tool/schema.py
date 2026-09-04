def get_schema() -> dict:
    """Vulnerable mode: raw path string joined naively against the workspace
    root with no normalization/containment check -- classic ../../ traversal,
    deliberately left in (see attacks/01/attack_param_manipulation.py)."""
    return {
        "name": "file_tool",
        "description": "Read, write, or list files in the agent's workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "description": "read | write | list"},
                "path": {"type": "string"},
                "content": {"type": "string", "description": "required for write"},
            },
            "required": ["op", "path"],
        },
    }
