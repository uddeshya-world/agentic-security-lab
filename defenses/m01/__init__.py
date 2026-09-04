"""Module 1 defenses: schema validation, least privilege, approval gate, isolation."""

from defenses.m01.approval_gate import ApprovalDenied, require_approval
from defenses.m01.isolation import IsolationError, run_isolated
from defenses.m01.least_privilege import PrivilegeError, apply_least_privilege
from defenses.m01.schema_validation import SchemaValidationError, validate_step

__all__ = [
    "ApprovalDenied",
    "IsolationError",
    "PrivilegeError",
    "SchemaValidationError",
    "apply_least_privilege",
    "require_approval",
    "run_isolated",
    "validate_step",
]
