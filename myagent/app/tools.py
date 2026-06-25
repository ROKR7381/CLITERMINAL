from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List


# Workspace root: prevent tools from reading/writing outside the repo.
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def _resolve_within_workspace(path: str) -> Path:
    """Resolve a user-supplied path and ensure it stays within the workspace."""
    p = Path(path)
    if not p.is_absolute():
        p = WORKSPACE_ROOT / p
    p = p.resolve()
    if WORKSPACE_ROOT not in p.parents and p != WORKSPACE_ROOT:
        raise PermissionError("Path escapes workspace")
    return p


def read_file(path: str) -> str:
    p = _resolve_within_workspace(path)
    if p.is_dir():
        raise IsADirectoryError(str(p))
    return p.read_text(encoding="utf-8", errors="replace")


def write_file(path: str, content: str) -> str:
    p = _resolve_within_workspace(path)
    if p.is_dir():
        raise IsADirectoryError(str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {p}"


def list_dir(path: str = ".") -> List[str]:
    p = _resolve_within_workspace(path)
    if not p.is_dir():
        raise NotADirectoryError(str(p))
    entries = []
    for child in sorted(p.iterdir(), key=lambda x: x.name.lower()):
        suffix = "/" if child.is_dir() else ""
        entries.append(child.name + suffix)
    return entries


def run_shell(cmd: str, timeout_s: int = 30) -> str:
    """Run a shell command within workspace root."""
    # Avoid implicit shell parsing where possible, but keep compatibility.
    proc = subprocess.run(
        cmd,
        cwd=str(WORKSPACE_ROOT),
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    out = proc.stdout or ""
    err = proc.stderr or ""
    if proc.returncode != 0:
        return out + ("\n" if out and err else "") + err + f"\n(exit code {proc.returncode})"
    return out if out else err


def search_text(path: str, keyword: str, max_results: int = 50) -> str:
    """Naive text search to avoid external ripgrep dependency."""
    base = _resolve_within_workspace(path)
    if base.is_file():
        candidates = [base]
    else:
        candidates = [p for p in base.rglob("*") if p.is_file()]

    keyword_lower = keyword.lower()
    results = []

    for file_path in candidates:
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if keyword_lower not in text.lower():
            continue

        # Provide a few matching lines.
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if keyword_lower in line.lower():
                rel = str(file_path.relative_to(WORKSPACE_ROOT))
                results.append(f"{rel}:{i}: {line}")
                if len(results) >= max_results:
                    return "\n".join(results)

    return "\n".join(results) if results else "No matches"


