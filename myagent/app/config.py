import os
import re
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def _sync_settings_api_key(api_key: str | None) -> str | None:
    settings.api_key = api_key
    return api_key


def _save_api_key(env_path: Path, api_key: str) -> None:
    line = f"OPENAI_API_KEY={api_key}"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if re.search(r"(?m)^OPENAI_API_KEY=.*$", content):
            content = re.sub(r"(?m)^OPENAI_API_KEY=.*$", line, content)
        else:
            if content and not content.endswith(("\n", "\r")):
                content += "\n"
            content += f"{line}\n"
        env_path.write_text(content, encoding="utf-8")
        return

    env_path.write_text(f"{line}\n", encoding="utf-8")


def ensure_api_key(force_prompt: bool = False) -> str | None:
    """Check for API key and prompt user on first run if missing."""
    env_path = Path(".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and not force_prompt:
        return _sync_settings_api_key(api_key)

    if env_path.exists() and not force_prompt:
        load_dotenv(env_path, override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return _sync_settings_api_key(api_key)

    print("\nPlease paste your OpenAI API key:")
    try:
        api_key = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n[yellow]No API key provided. Some features may not work.[/yellow]")
        return _sync_settings_api_key(None)

    if not api_key:
        print("[yellow]No API key provided. Some features may not work.[/yellow]")
        return _sync_settings_api_key(None)

    _save_api_key(env_path, api_key)
    os.environ["OPENAI_API_KEY"] = api_key
    print("✅ Saved! Starting CLI...\n")
    return _sync_settings_api_key(api_key)

AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]


class Settings(BaseModel):
    app_name: str = "myagent"
    model: str = os.getenv("MYAGENT_MODEL", "gpt-4o-mini")
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    session_dir: str = os.getenv("MYAGENT_SESSION_DIR", "data/sessions")
    agent_dir: str = os.getenv("MYAGENT_AGENT_DIR", "agents")
    plan_mode: bool = False
    edit_mode: bool = True
    approval_required: bool = True


settings = Settings()
