import json
import uuid
from pathlib import Path
from app.config import settings


def ensure_dir():
    Path(settings.session_dir).mkdir(parents=True, exist_ok=True)


def save_session(messages, agent_name="default") -> str:
    ensure_dir()
    sid = str(uuid.uuid4())[:8]
    path = Path(settings.session_dir) / f"{agent_name}_{sid}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    return sid


def load_session(session_id: str) -> list:
    for file in Path(settings.session_dir).glob(f"*{session_id}*.json"):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def list_sessions() -> list[str]:
    return [f.stem for f in Path(settings.session_dir).glob("*.json")]


