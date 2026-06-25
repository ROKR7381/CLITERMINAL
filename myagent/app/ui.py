from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from pathlib import Path


def build_prompt():
    Path(".myagent").mkdir(exist_ok=True)
    commands = [
        "/init", "/help", "/exit", "/model", "/plan", "/edit", "/approve",
        "/commands",
        "/save", "/load", "/agent", "/agents", "/skills", "/skill", "/fix",
        "/project", "/clear", "/tools", "/read", "/write", "/ls", "/shell", "/search"
    ]
    return PromptSession(
        history=FileHistory(".myagent/history.txt"),
        completer=WordCompleter(commands, ignore_case=True),
        multiline=False,
    )


