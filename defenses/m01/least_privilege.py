"""Least-privilege helpers used by the executor under SECURE_MODE.

Tool servers already enforce secure branches (parameterized DB, path jail,
email domain allow-list). This module re-states scope checks so the agent
choke point fails closed even if a tool were misconfigured.
"""
from __future__ import annotations

ALLOWED_EMAIL_DOMAINS = frozenset({"example.test"})


class PrivilegeError(PermissionError):
    pass


def enforce_db_scope(args: dict) -> dict:
    """Normalize db_tool args to secure shape: table + customer_id only."""
    table = args.get("table")
    if table not in {"customers", "orders"}:
        raise PrivilegeError(f"db table '{table}' out of scope")
    if "customer_id" not in args:
        raise PrivilegeError("customer_id required for least-privilege db access")
    return {"table": table, "customer_id": int(args["customer_id"])}


def enforce_email_scope(args: dict) -> dict:
    to = args.get("to", "")
    domain = to.split("@")[-1].lower() if "@" in to else ""
    if domain not in ALLOWED_EMAIL_DOMAINS:
        raise PrivilegeError(f"recipient domain '{domain}' not allow-listed")
    return args


def enforce_file_scope(args: dict) -> dict:
    path = str(args.get("path", ""))
    normalized = path.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("~"):
        raise PrivilegeError("absolute paths not allowed")
    if ".." in normalized.split("/"):
        raise PrivilegeError("path traversal segments not allowed")
    return args


def apply_least_privilege(tool: str, args: dict) -> dict:
    if tool == "db_tool":
        return enforce_db_scope(args)
    if tool == "email_tool":
        return enforce_email_scope(args)
    if tool == "file_tool":
        return enforce_file_scope(args)
    return args
