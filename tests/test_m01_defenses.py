"""Unit tests for Module 1 defenses (no Docker required)."""
import os

import pytest

from defenses.m01.approval_gate import ApprovalDenied, require_approval
from defenses.m01.least_privilege import PrivilegeError, apply_least_privilege
from defenses.m01.schema_validation import SchemaValidationError, validate_step


def test_schema_rejects_unknown_tool():
    with pytest.raises(SchemaValidationError):
        validate_step("shell_tool", {})


def test_schema_db_requires_customer_id():
    with pytest.raises(SchemaValidationError):
        validate_step("db_tool", {"table": "customers", "filter": "1=1"})


def test_schema_db_accepts_scoped():
    validate_step("db_tool", {"table": "customers", "customer_id": 1})


def test_schema_rejects_path_dots():
    with pytest.raises(SchemaValidationError):
        validate_step("file_tool", {"op": "read", "path": "../etc/hostname"})


def test_least_privilege_email_blocks_external():
    with pytest.raises(PrivilegeError):
        apply_least_privilege(
            "email_tool",
            {"to": "audit@external-logging.test", "subject": "x", "body": "y"},
        )


def test_least_privilege_email_allows_lab_domain():
    apply_least_privilege(
        "email_tool",
        {"to": "user@example.test", "subject": "x", "body": "y"},
    )


def test_approval_denies_email_without_lab_approve(monkeypatch):
    monkeypatch.delenv("LAB_APPROVE", raising=False)
    with pytest.raises(ApprovalDenied):
        require_approval("email_tool", {"to": "a@example.test", "subject": "s", "body": "b"})


def test_approval_allows_with_lab_approve(monkeypatch):
    monkeypatch.setenv("LAB_APPROVE", "1")
    require_approval("email_tool", {"to": "a@example.test", "subject": "s", "body": "b"})


def test_file_path_jail_logic(tmp_path):
    from pathlib import Path

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "ok.txt").write_text("hi", encoding="utf-8")

    def resolve_secure(path: str) -> Path:
        candidate = (workspace / path).resolve()
        candidate.relative_to(workspace.resolve())
        return candidate

    assert resolve_secure("ok.txt").name == "ok.txt"
    with pytest.raises(ValueError):
        resolve_secure("../outside.txt")
