import os
from pathlib import Path

from tools.base import InvokeResult, is_secure, make_tool_app
from tools.file_tool.schema import get_schema

WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", "/workspace"))
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_vulnerable(path: str) -> Path:
    """Naive join -- no normalization/containment check. `../../etc/hostname`
    escapes WORKSPACE_DIR here on purpose."""
    return Path(os.path.join(str(WORKSPACE_DIR), path))


def _resolve_secure(path: str) -> Path:
    """Resolve path and reject anything outside WORKSPACE_DIR via relative_to."""
    workspace_resolved = WORKSPACE_DIR.resolve()
    # Disallow absolute paths that ignore workspace join semantics.
    candidate = (WORKSPACE_DIR / path).resolve()
    try:
        candidate.relative_to(workspace_resolved)
    except ValueError as e:
        raise PermissionError(f"path '{path}' escapes workspace jail") from e
    return candidate


def _invoke(args: dict) -> InvokeResult:
    op = args.get("op", "")
    path = args.get("path", "")
    content = args.get("content", "")

    try:
        resolved = _resolve_secure(path) if is_secure() else _resolve_vulnerable(path)
    except PermissionError as e:
        return InvokeResult(result={"error": str(e)}, side_effects=[])

    if op == "write":
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content)
        return InvokeResult(
            result={"written": True, "resolved_path": str(resolved)},
            side_effects=[{"type": "file_write", "resolved_path": str(resolved)}],
        )
    elif op == "read":
        if not resolved.exists():
            return InvokeResult(result={"error": "not found", "resolved_path": str(resolved)})
        return InvokeResult(
            result={"content": resolved.read_text(errors="replace"), "resolved_path": str(resolved)},
            side_effects=[{"type": "file_read", "resolved_path": str(resolved)}],
        )
    elif op == "list":
        base = resolved if resolved.is_dir() else resolved.parent
        entries = [p.name for p in base.iterdir()] if base.exists() else []
        return InvokeResult(result={"entries": entries, "resolved_path": str(base)})
    else:
        return InvokeResult(result={"error": f"unknown op '{op}'"})


app = make_tool_app("file_tool", get_schema, _invoke)
