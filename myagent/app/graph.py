from langgraph.graph import StateGraph, START, END
from rich import print
from rich.markdown import Markdown

from app.state import AgentState
from app.models import OpenAIProvider
from app.streaming import stream_response
from app.pricing import calculate_cost
from app.config import settings
from app.agents import load_agent
from app.skills import list_skills


def _get_provider() -> OpenAIProvider:
    return OpenAIProvider()


def answer_node(state: AgentState) -> AgentState:
    user_input = state.get("user_input", "")
    system_prompt = state.get("system_prompt", "")
    agent_name = state.get("agent_name", "default")

    agent = load_agent(agent_name)
    agent_skills = agent.get("skills", [])

    skills_text = "\n".join([f"- {s}" for s in agent_skills]) if agent_skills else "None"

    full_system = f"""{system_prompt}

You are agent: {agent_name}.
You have access to these SKILLS:
{skills_text}

When user asks something that matches a skill, suggest using:
/skill <skill_name> <input>
"""

    provider = _get_provider()
    result = provider.generate(user_input, full_system)
    text = result["text"]
    tokens_in = result["tokens_in"]
    tokens_out = result["tokens_out"]
    cost = calculate_cost(settings.model, tokens_in, tokens_out)

    if text.strip():
        print()
        print("[bold green]Assistant:[/bold green]")
        print(Markdown(text))

    print(f"\n[dim]Tokens: {tokens_in} in / {tokens_out} out | Cost: ${cost:.6f} | Model: {settings.model}[/dim]")

    messages = state.get("messages", [])
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": text})

    return {
        "messages": messages,
        "answer": text,
        "should_retry": False,
    }


def judge_node(state: AgentState) -> AgentState:
    return {"should_retry": not bool(state.get("answer", "").strip())}


def route_after_judge(state: AgentState):
    return "answer" if state.get("should_retry") else END


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("answer", answer_node)
    g.add_node("judge", judge_node)

    g.add_edge(START, "answer")
    g.add_edge("answer", "judge")
    g.add_conditional_edges("judge", route_after_judge)

    return g.compile()



