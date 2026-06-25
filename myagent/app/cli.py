import argparse
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.table import Table
from app.graph import build_graph
from app.ui import build_prompt
from app.sessions import save_session, load_session, list_sessions
from app.agents import load_agent, list_agents
from app.tools import read_file, write_file, list_dir, run_shell, search_text
from app.permissions import is_allowed
from app.config import settings, AVAILABLE_MODELS, ensure_api_key

console = Console()

COMMANDS_INFO = [
    ("/init", "Scan project and build AGENTS.md"),
    ("/help", "Show help"),
    ("/exit", "Exit CLI"),
    ("/model", "Switch AI model"),
    ("/plan", "Toggle plan mode"),
    ("/edit", "Toggle edit mode"),
    ("/approve", "Toggle approval mode"),
    ("/save", "Save session"),
    ("/load", "Load session by id"),
    ("/agents", "List agents"),
    ("/agent", "Switch agent"),
    ("/skills", "List skills"),
    ("/skill", "Run skill"),
    ("/fix", "Review and auto-fix file"),
    ("/project", "Summarize project"),
    ("/tools", "Show available tools"),
    ("/read", "Read file"),
    ("/write", "Write file"),
    ("/ls", "List directory"),
    ("/shell", "Run shell command"),
    ("/search", "Search in files"),
    ("/clear", "Clear messages"),
]


def pick_model_interactively() -> str | None:
    # Try an arrow-key based picker first so users get a clear pointer/highlight.
    try:
        from prompt_toolkit.shortcuts import radiolist_dialog

        values = [(m, m) for m in AVAILABLE_MODELS]
        return radiolist_dialog(
            title="Select Model",
            text="Use Up/Down arrows, then Enter on OK to apply.",
            values=values,
            default=settings.model,
            ok_text="Select",
            cancel_text="Cancel",
        ).run()
    except Exception:
        # Fallback for environments where the dialog cannot be rendered.
        print("[cyan]Available models:[/cyan]")
        for i, m in enumerate(AVAILABLE_MODELS, start=1):
            marker = "[bold green]*[/bold green]" if m == settings.model else " "
            print(f"{marker} {i}. {m}")
        try:
            choice = input("Select model number (blank to cancel): ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(AVAILABLE_MODELS):
                return AVAILABLE_MODELS[idx]
        except (ValueError, KeyboardInterrupt, EOFError):
            return None
    return None


def pick_command_interactively() -> str | None:
    try:
        from prompt_toolkit.shortcuts import radiolist_dialog

        values = [(cmd, f"{cmd:<10} {desc}") for cmd, desc in COMMANDS_INFO]
        return radiolist_dialog(
            title="Select Command",
            text="Use Up/Down arrows, then Enter on Select.",
            values=values,
            default="/help",
            ok_text="Select",
            cancel_text="Cancel",
        ).run()
    except Exception:
        print("[cyan]Available commands:[/cyan]")
        for i, (cmd, desc) in enumerate(COMMANDS_INFO, start=1):
            print(f" {i:>2}. {cmd:<10} {desc}")
        try:
            choice = input("Select command number (blank to cancel): ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(COMMANDS_INFO):
                return COMMANDS_INFO[idx][0]
        except (ValueError, KeyboardInterrupt, EOFError):
            return None
    return None


def resolve_command_args(selected: str) -> str | None:
    try:
        if selected == "/load":
            sid = input("Session id: ").strip()
            return f"/load {sid}" if sid else None
        if selected == "/agent":
            name = input("Agent name: ").strip()
            return f"/agent use {name}" if name else None
        if selected == "/skill":
            args = input("Skill input (<name> <input>): ").strip()
            return f"/skill {args}" if args else None
        if selected == "/fix":
            args = input("Fix input (<skill> <file>): ").strip()
            return f"/fix {args}" if args else None
        if selected == "/read":
            path = input("File path: ").strip()
            return f"/read {path}" if path else None
        if selected == "/write":
            path = input("File path: ").strip()
            if not path:
                return None
            text = input("Text: ").strip()
            return f"/write {path} {text}" if text else None
        if selected == "/ls":
            path = input("Directory path (blank for .): ").strip()
            return f"/ls {path}" if path else "/ls"
        if selected == "/shell":
            cmd = input("Shell command: ").strip()
            return f"/shell {cmd}" if cmd else None
        if selected == "/search":
            args = input("Search input (<path> <keyword>): ").strip()
            return f"/search {args}" if args else None
    except (KeyboardInterrupt, EOFError):
        return None
    return selected

HELP = """[bold cyan]+-----------------------------------------------+
|           [bold white]Available Commands[/bold white]                |
+-----------------------------------------------+
|  [yellow]/init[/yellow]              Scan project & build AGENTS.md |
|  [yellow]/help[/yellow]              Show this help         |
|  [yellow]/commands[/yellow]          Open command picker    |
|  [yellow]/exit[/yellow]              Exit CLI               |
|  [yellow]/model[/yellow]             Switch AI model        |
|  [yellow]/plan[/yellow]              Toggle plan mode       |
|  [yellow]/edit[/yellow]              Toggle edit mode       |
|  [yellow]/approve[/yellow]           Toggle approval mode   |
|  [yellow]/save[/yellow]              Save session           |
|  [yellow]/load[/yellow] [green]<id>[/green]         Load session           |
|  [yellow]/agents[/yellow]            List agents            |
|  [yellow]/agent[/yellow] [green]use <name>[/green]  Switch agent            |
|  [yellow]/skills[/yellow]            List skills            |
|  [yellow]/skill[/yellow] [green]<name> <input>[/green] Run a skill       |
|  [yellow]/fix[/yellow] [green]<skill> <file>[/green] Review & auto-fix file |
|  [yellow]/project[/yellow]           Summarize project      |
|  [yellow]/tools[/yellow]             Show available tools   |
|  [yellow]/read[/yellow] [green]<path>[/green]       Read file               |
|  [yellow]/write[/yellow] [green]<path> <txt>[/green] Write file               |
|  [yellow]/ls[/yellow] [green]<path>[/green]         List directory          |
|  [yellow]/shell[/yellow] [green]<cmd>[/green]       Run shell command       |
|  [yellow]/search[/yellow] [green]<path> <kw>[/green] Search in files         |
|  [yellow]/clear[/yellow]            Clear messages         |
+-----------------------------------------------+[/bold cyan]"""


def show_banner():
    console.print()
    
    banner = Text()
    banner.append(" __  __  ________  _________    ___   ____\n", style="bold cyan")
    banner.append("|\\  \\|\\  \\|\\   __  \\|\\___   ___\\ |\\  \\ |\\  _\\\n", style="bold cyan")
    banner.append("| \\   \\\\\\  \\| \\  \\ \\  |___ \\  \\_| \\ \\  \\\\|__/|\n", style="bold cyan")
    banner.append("| \\   \\|\\  | \\  \\ \\  |   \\ \\  \\ | \\   \\\\|__|\n", style="bold cyan")
    banner.append("| \\   \\\\  | \\  \\_\\  |    \\ \\  \\ | \\   \\    |\n", style="bold cyan")
    banner.append("| \\___\\ \\  | \\_______|     \\ \\__| \\ \\__\\ \\__|\n", style="bold cyan")
    banner.append("|_______|__|__________|______\\|__|  \\|__|\\|__|\n", style="bold cyan")
    
    console.print(Align.center(banner))
    
    subtitle = Text("  Interactive AI Agent Framework", style="bold white")
    console.print(Align.center(subtitle))
    console.print()

    mode_status = []
    if settings.plan_mode:
        mode_status.append("[yellow]PLAN[/yellow]")
    if settings.edit_mode:
        mode_status.append("[green]EDIT[/green]")
    if settings.approval_required:
        mode_status.append("[cyan]APPROVE[/cyan]")
    modes = " ".join(mode_status) if mode_status else "[dim]None[/dim]"

    console.print(Panel.fit(
        f"[bold green]MyAgent CLI[/bold green]\n"
        f"[white]Version [cyan]1.0.0[/cyan] | Model: [yellow]{settings.model}[/yellow][/white]\n"
        f"[white]Modes: {modes}[/white]\n"
        f"[white]Type [yellow]/help[/yellow] to see commands[/white]",
        border_style="bright_cyan",
        title="/welcome",
        title_align="left",
        padding=(0, 2),
    ))


def approve_action(action: str, details: str) -> bool:
    if not settings.approval_required:
        return True
    print(f"[yellow]APPROVAL REQUIRED:[/yellow] {action}")
    print(f"[dim]{details}[/dim]")
    try:
        response = input("Approve? (y/n): ").strip().lower()
        return response in ("y", "yes", "")
    except (KeyboardInterrupt, EOFError):
        return False


def handle_command(cmd: str, state: dict) -> bool:
    parts = cmd.strip().split(maxsplit=2)
    if not parts:
        return True

    head = parts[0]

    if head == "/exit":
        return False
    elif head == "/init":
        from app.context import scan_repo, build_agents_md
        summary = scan_repo(".")
        md = build_agents_md(summary)
        with open("AGENTS.md", "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[green]AGENTS.md created with {summary['total_files']} files scanned[/green]")
    elif head in ("/help", "/commands"):
        print(HELP)
        selected = pick_command_interactively()
        if selected and selected not in ("/help", "/commands"):
            resolved = resolve_command_args(selected)
            if resolved:
                return handle_command(resolved, state)
    elif head == "/model":
        if len(parts) >= 2 and parts[1] in AVAILABLE_MODELS:
            settings.model = parts[1]
            print(f"[green]Model switched to:[/green] {settings.model}")
        else:
            selected = pick_model_interactively()
            if selected and selected in AVAILABLE_MODELS:
                settings.model = selected
                print(f"[green]Model switched to:[/green] {settings.model}")
            else:
                table = Table(title="Available Models")
                table.add_column("Model", style="cyan")
                table.add_column("Status", style="green")
                for m in AVAILABLE_MODELS:
                    status = "[bold green]ACTIVE[/bold green]" if m == settings.model else ""
                    table.add_row(m, status)
                console.print(table)
                print("[dim]Tip: use /model <name> or run /model to open selector.[/dim]")
    elif head == "/plan":
        settings.plan_mode = not settings.plan_mode
        status = "[green]ON[/green]" if settings.plan_mode else "[red]OFF[/red]"
        print(f"[cyan]Plan mode:[/cyan] {status}")
    elif head == "/edit":
        settings.edit_mode = not settings.edit_mode
        status = "[green]ON[/green]" if settings.edit_mode else "[red]OFF[/red]"
        print(f"[cyan]Edit mode:[/cyan] {status}")
    elif head == "/approve":
        settings.approval_required = not settings.approval_required
        status = "[green]ON[/green]" if settings.approval_required else "[red]OFF[/red]"
        print(f"[cyan]Approval mode:[/cyan] {status}")
    elif head == "/agents":
        print(list_agents())
    elif head == "/agent" and len(parts) >= 3 and parts[1] == "use":
        agent = load_agent(parts[2])
        state["agent_name"] = agent["name"]
        state["system_prompt"] = agent["system_prompt"]
        state["permissions"] = agent["permissions"]
        print(f"[green]Switched to agent:[/green] {agent['name']}")
    elif head == "/save":
        sid = save_session(state["messages"], state.get("agent_name", "default"))
        print(f"[yellow]Saved session ID:[/yellow] {sid}")
    elif head == "/load" and len(parts) >= 2:
        state["messages"] = load_session(parts[1])
        print(f"[green]Loaded {len(state['messages'])} messages[/green]")
    elif head == "/tools":
        print(state.get("permissions", []))
    elif head == "/skills":
        from app.skills import list_skills
        skills = list_skills()
        if skills:
            print("[cyan]Available skills:[/cyan]")
            for s in skills:
                print(f"  [yellow]{s}[/yellow]")
        else:
            print("[dim]No skills found[/dim]")
    elif head == "/skill" and len(parts) >= 3:
        from app.skills import run_skill, load_skill, is_file_path
        from app.models import OpenAIProvider
        skill_name = parts[1]
        skill_input = parts[2]
        skill = load_skill(skill_name)
        if not skill:
            print(f"[red]Skill '{skill_name}' not found[/red]")
        else:
            provider = OpenAIProvider()
            inputs = {inp: skill_input for inp in skill.get("inputs", ["text"])}
            result = run_skill(skill_name, inputs, provider)
            if is_file_path(skill_input):
                print(f"[cyan]File:[/cyan] {skill_input}")
            print(f"[green]Skill {skill_name} result:[/green]\n{result}")
    elif head == "/fix" and len(parts) >= 3:
        from app.skills import run_skill_with_fix, load_skill, is_file_path
        from app.models import OpenAIProvider
        skill_name = parts[1]
        file_path = parts[2]
        skill = load_skill(skill_name)
        if not skill:
            print(f"[red]Skill '{skill_name}' not found[/red]")
        else:
            provider = OpenAIProvider()
            inputs = {inp: file_path for inp in skill.get("inputs", ["text"])}
            result, fixed_path = run_skill_with_fix(skill_name, inputs, provider, auto_fix=True)
            if fixed_path:
                print(f"[green]File auto-fixed:[/green] {fixed_path}")
            print(f"[green]Review:[/green]\n{result}")
    elif head == "/project":
        from app.context import scan_repo
        from app.skills import run_skill, load_skill
        from app.models import OpenAIProvider
        from pathlib import Path
        summary = scan_repo(".")
        code_content = ""
        for f in summary["files"][:10]:
            try:
                content = Path(f).read_text(encoding="utf-8", errors="ignore")
                code_content += f"\n--- {f} ---\n{content[:500]}\n"
            except:
                pass
        provider = OpenAIProvider()
        skill = load_skill("summarize")
        prompt = skill["prompt"].replace("{text}", code_content)
        result = provider.generate(prompt, system="")
        text = result["text"] if isinstance(result, dict) else result
        print(f"[green]Project Summary:[/green]\n{text}")
    elif head == "/read" and len(parts) >= 2:
        if is_allowed("read", state["permissions"]):
            print(read_file(parts[1]))
        else:
            print("[red]Permission denied: read[/red]")
    elif head == "/write" and len(parts) >= 3:
        if is_allowed("write", state["permissions"]):
            if approve_action("write file", f"Write to {parts[1]}"):
                print(write_file(parts[1], parts[2]))
            else:
                print("[yellow]Write cancelled[/yellow]")
        else:
            print("[red]Permission denied: write[/red]")
    elif head == "/ls":
        path = parts[1] if len(parts) >= 2 else "."
        if is_allowed("list", state["permissions"]):
            print(list_dir(path))
        else:
            print("[red]Permission denied: list[/red]")
    elif head == "/shell" and len(parts) >= 2:
        if is_allowed("shell", state["permissions"]):
            cmd_str = " ".join(parts[1:])
            if approve_action("shell command", f"Run: {cmd_str}"):
                print(run_shell(cmd_str))
            else:
                print("[yellow]Shell cancelled[/yellow]")
        else:
            print("[red]Permission denied: shell[/red]")
    elif head == "/search" and len(parts) >= 3:
        if is_allowed("search", state["permissions"]):
            print(search_text(parts[1], parts[2]))
        else:
            print("[red]Permission denied: search[/red]")
    elif head == "/clear":
        state["messages"] = []
        print("[yellow]Cleared messages[/yellow]")
    else:
        print("[red]Unknown command. Type /help[/red]")
    return True


def interactive():
    ensure_api_key()
    show_banner()

    from app.context import scan_repo
    summary = scan_repo(".")
    print(f"[cyan]Detected project:[/cyan] {summary['project_type']} "
          f"([yellow]{summary['total_files']} files[/yellow])")

    graph = build_graph()
    prompt = build_prompt()

    default_agent = load_agent("default")
    state = {
        "messages": [],
        "agent_name": default_agent["name"],
        "system_prompt": default_agent["system_prompt"],
        "permissions": default_agent["permissions"],
    }

    while True:
        try:
            agent_name = state['agent_name']
            text = prompt.prompt(f"({agent_name}) > ")
        except (KeyboardInterrupt, EOFError):
            break

        if not text.strip():
            continue

        if text.startswith("/"):
            ok = handle_command(text, state)
            if not ok:
                break
            continue

        if settings.plan_mode:
            from app.models import OpenAIProvider
            provider = OpenAIProvider()
            plan_prompt = f"""Create a step-by-step plan for this task:
{text}

Respond with numbered steps only."""
            result = provider.generate(plan_prompt, system="You are a planning assistant.")
            plan = result["text"] if isinstance(result, dict) else result
            print(f"\n[cyan]PLAN:[/cyan]\n{plan}")
            if settings.approval_required:
                try:
                    response = input("\nProceed with plan? (y/n): ").strip().lower()
                    if response not in ("y", "yes", ""):
                        print("[yellow]Plan cancelled[/yellow]")
                        continue
                except (KeyboardInterrupt, EOFError):
                    break

        result = graph.invoke({
            "user_input": text,
            "messages": state["messages"],
            "system_prompt": state["system_prompt"],
            "permissions": state["permissions"],
            "agent_name": state["agent_name"],
        })

        state["messages"] = result.get("messages", state["messages"])


def main():
    parser = argparse.ArgumentParser(prog="myagent")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("tui")
    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("text", type=str)

    args = parser.parse_args()

    if args.command == "tui":
        from app.tui import run_tui
        run_tui()
    elif args.command == "run":
        graph = build_graph()
        agent = load_agent("default")
        graph.invoke({
            "user_input": args.text,
            "messages": [],
            "system_prompt": agent["system_prompt"],
            "permissions": agent["permissions"],
            "agent_name": agent["name"],
        })
    else:
        interactive()


if __name__ == "__main__":
    main()
