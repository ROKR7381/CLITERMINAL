from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    user_input: str
    messages: List[Dict[str, Any]]
    answer: str
    tool_calls: List[Dict[str, Any]]
    agent_name: str
    system_prompt: str
    permissions: List[str]
    should_retry: bool
    error: str


