import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

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
