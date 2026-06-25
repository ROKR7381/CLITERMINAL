import os
from pathlib import Path

IGNORE_DIRS = {".git", "venv", "node_modules", "__pycache__", ".idea", ".vscode"}
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp", ".c", ".cs", ".html", ".css"}


def detect_project_type(root="."):
    files = os.listdir(root)
    if "package.json" in files:
        return "Node.js"
    if "requirements.txt" in files or "pyproject.toml" in files:
        return "Python"
    if "pom.xml" in files:
        return "Java"
    if "go.mod" in files:
        return "Go"
    if "Cargo.toml" in files:
        return "Rust"
    return "Unknown"


def scan_repo(root="."):
    summary = {
        "project_type": detect_project_type(root),
        "files": [],
        "total_files": 0,
        "languages": {},
    }

    for path in Path(root).rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            ext = path.suffix
            if ext in CODE_EXTS:
                summary["files"].append(str(path))
                summary["languages"][ext] = summary["languages"].get(ext, 0) + 1
                summary["total_files"] += 1

    return summary


def build_agents_md(summary):
    md = "# AGENTS.md\n\n"
    md += f"## Project Type\n{summary['project_type']}\n\n"
    md += f"## Total Code Files\n{summary['total_files']}\n\n"
    md += "## Languages\n"
    for ext, count in summary["languages"].items():
        md += f"- {ext} -> {count} files\n"
    md += "\n## Suggested Agents\n"
    md += "- code_reviewer\n- file_explorer\n- shell_helper\n"
    return md
