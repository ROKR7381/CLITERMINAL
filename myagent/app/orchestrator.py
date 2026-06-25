from app.agents import load_agent, list_agents
from app.models import OpenAIProvider
from app.memory import memory


class AgentOrchestrator:
    def __init__(self):
        self.provider = OpenAIProvider()
        self.agents = {}
        for name in list_agents():
            self.agents[name] = load_agent(name)

    def route_task(self, user_input: str, current_agent: str) -> str:
        agent_list = "\n".join([f"- {name}: {a.get('description', '')}" for name, a in self.agents.items()])
        
        route_prompt = f"""You are an orchestrator. Route this task to the best agent.

Available agents:
{agent_list}

User task: {user_input}

Respond with ONLY the agent name (e.g., "code_reviewer" or "default")."""
        
        result = self.provider.generate(route_prompt, system="You route tasks to agents.")
        recommended = result["text"].strip().lower()
        
        if recommended in self.agents:
            return recommended
        return current_agent

    def delegate_to_agent(self, agent_name: str, user_input: str, messages: list) -> dict:
        agent = self.agents.get(agent_name, self.agents.get("default"))
        
        context = memory.get_context(user_input)
        context_section = f"\n\nProject Context:\n{context}" if context else ""
        
        system = agent.get("system_prompt", "") + context_section
        
        result = self.provider.generate(user_input, system=system)
        return {
            "agent": agent_name,
            "answer": result["text"],
            "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0),
        }

    def multi_agent_run(self, user_input: str, current_agent: str, messages: list) -> dict:
        best_agent = self.route_task(user_input, current_agent)
        
        if best_agent != current_agent:
            from rich import print
            print(f"[cyan]Orchestrator:[/cyan] Routing to [yellow]{best_agent}[/yellow]")
        
        return self.delegate_to_agent(best_agent, user_input, messages)


orchestrator = AgentOrchestrator()
