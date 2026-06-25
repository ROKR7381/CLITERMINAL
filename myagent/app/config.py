import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def ensure_api_key() -> str | None:
    """Check for API key and prompt user on first run if missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path, override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key

    print("\n👋 Welcome! Please paste your Open API key:")
    try:
        api_key = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n[yellow]No API key provided. Some features may not work.[/yellow]")
        return None

    if not api_key:
        print("[yellow]No API key provided. Some features may not work.[/yellow]")
        return None

    with open(env_path, "a", encoding="utf-8") as f:
        f.write(f"\nOPENAI_API_KEY={api_key}\n")

    os.environ["OPENAI_API_KEY"] = api_key
    print("✅ Saved! Starting CLI...\n")
    return api_key

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
