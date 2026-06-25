import yaml
from pathlib import Path
from app.config import settings


def list_agents() -> list[str]:
    p = Path(settings.agent_dir)
    if not p.exists():
        return []
    return [f.stem for f in p.glob("*.yaml")]


def load_agent(name: str) -> dict:
    path = Path(settings.agent_dir) / f"{name}.yaml"
    if not path.exists():
        return {
            "name": "default",
            "description": "Generic AI assistant",
            "system_prompt": "You are a helpful AI assistant.",
            "permissions": ["read", "write", "shell", "search", "list"],
        }
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


