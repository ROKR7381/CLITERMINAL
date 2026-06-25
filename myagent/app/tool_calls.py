import json
from app.tools import read_file, write_file, list_dir, run_shell, search_text

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string", "description": "Shell command to run"},
                },
                "required": ["cmd"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Search for text in files",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory or file to search"},
                    "keyword": {"type": "string", "description": "Search keyword"},
                },
                "required": ["path", "keyword"],
            },
        },
    },
]

TOOL_MAP = {
    "read_file": lambda path: read_file(path),
    "write_file": lambda path, content: write_file(path, content),
    "list_dir": lambda path="\\.": list_dir(path),
    "run_shell": lambda cmd: run_shell(cmd),
    "search_text": lambda path, keyword: search_text(path, keyword),
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    try:
        if tool_name not in TOOL_MAP:
            return f"Unknown tool: {tool_name}"
        result = TOOL_MAP[tool_name](**arguments)
        return str(result) if not isinstance(result, str) else result
    except Exception as e:
        return f"Error: {str(e)}"


def get_tools_for_agent(agent_permissions: list) -> list:
    allowed_tools = []
    permission_map = {
        "read": ["read_file", "list_dir"],
        "write": ["write_file"],
        "shell": ["run_shell"],
        "search": ["search_text"],
        "list": ["list_dir"],
    }
    for perm in agent_permissions:
        allowed_tools.extend(permission_map.get(perm, []))
    return [t for t in TOOL_DEFINITIONS if t["function"]["name"] in set(allowed_tools)]
