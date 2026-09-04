"""Strict tool + arg checks applied at the executor choke point when SECURE_MODE=true."""
from __future__ import annotations

ALLOWED_TOOLS = frozenset({"db_tool", "email_tool", "file_tool", "answer"})

# Per-tool allowed argument keys (deny unknown / injection-shaped extras).
ALLOWED_ARGS: dict[str, frozenset[str]] = {
    "db_tool": frozenset({"table", "customer_id", "filter"}),
    "email_tool": frozenset({"to", "subject", "body"}),
    "file_tool": frozenset({"op", "path", "content"}),
    "answer": frozenset({"text"}),
}

ALLOWED_TABLES = frozenset({"customers", "orders"})
ALLOWED_FILE_OPS = frozenset({"read", "write", "list"})


class SchemaValidationError(ValueError):
    pass


def validate_step(tool: str, args: dict | None) -> None:
    """Raise SchemaValidationError if tool/args are not allowed under secure mode."""
    args = args or {}
    if tool not in ALLOWED_TOOLS:
        raise SchemaValidationError(f"tool '{tool}' is not on the allow-list")

    allowed_keys = ALLOWED_ARGS[tool]
    unknown = set(args.keys()) - allowed_keys
    if unknown:
        raise SchemaValidationError(f"tool '{tool}' has unknown args: {sorted(unknown)}")

    if tool == "db_tool":
        table = args.get("table")
        if table not in ALLOWED_TABLES:
            raise SchemaValidationError(f"table '{table}' not allowed")
        # Secure path requires scoped customer_id; raw filter alone is rejected.
        if "customer_id" not in args:
            raise SchemaValidationError("db_tool requires customer_id in secure mode")
        try:
            int(args["customer_id"])
        except (TypeError, ValueError) as e:
            raise SchemaValidationError("customer_id must be an integer") from e
        filt = args.get("filter")
        if filt is not None and str(filt).strip() not in ("", f"customer_id = {args['customer_id']}"):
            # Reject free-form SQL fragments (injection surface).
            if any(tok in str(filt).lower() for tok in (" or ", "--", ";", "1=1", "union", "drop")):
                raise SchemaValidationError("db_tool filter rejected as potentially unsafe")

    if tool == "email_tool":
        for key in ("to", "subject", "body"):
            if key not in args or not isinstance(args[key], str) or not args[key]:
                raise SchemaValidationError(f"email_tool requires non-empty string '{key}'")

    if tool == "file_tool":
        op = args.get("op")
        if op not in ALLOWED_FILE_OPS:
            raise SchemaValidationError(f"file_tool op '{op}' not allowed")
        path = args.get("path")
        if not isinstance(path, str) or not path:
            raise SchemaValidationError("file_tool requires non-empty path")
        if ".." in path.replace("\\", "/").split("/"):
            raise SchemaValidationError("file_tool path must not contain '..' segments")
        if op == "write" and "content" not in args:
            raise SchemaValidationError("file_tool write requires content")
