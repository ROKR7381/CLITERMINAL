from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from app.graph import build_graph
from app.agents import list_agents, load_agent
from app.sessions import save_session, load_session, list_sessions
from app.skills import list_skills


# -------------------------------
# 1. Style for TUI
# -------------------------------
style = Style.from_dict({
    "frame.border": "#00afff",
    "title": "bg:#005f87 #ffffff bold",
    "toolbar": "bg:#222222 #00ffaf",
    "sidebar": "bg:#1c1c1c #ffffff",
    "chat": "bg:#000000 #ffffff",
    "tools": "bg:#080808 #ffaf00",
    "input": "bg:#000000 #00ff5f",
})


# -------------------------------
# 2. State
# -------------------------------
class TUIState:
    def __init__(self):
        self.graph = build_graph()
        self.agent = load_agent("default")
        self.messages = []
        self.tool_logs = []
        self.session_id = None


state = TUIState()


# -------------------------------
# 3. Sidebar Content
# -------------------------------
def get_sidebar_text():
    agents = list_agents() or ["default"]
    sessions = list_sessions() or ["(none)"]
    skills = list_skills() or ["(none)"]

    text = "<b>AGENTS</b>\n"
    for a in agents:
        marker = ">>>" if a == state.agent["name"] else "  "
        text += f"{marker} {a}\n"

    text += "\n<b>SKILLS</b>\n"
    for s in skills:
        text += f"* {s}\n"

    text += "\n<b>SESSIONS</b>\n"
    for s in sessions[-6:]:
        text += f"* {s}\n"

    return HTML(text)


# -------------------------------
# 4. Chat Pane
# -------------------------------
def get_chat_text():
    if not state.messages:
        return HTML("<i>Start chatting... type below and press Enter</i>")

    out = ""
    for m in state.messages[-20:]:
        if m["role"] == "user":
            out += f"<ansigreen><b>You:</b></ansigreen> {m['content']}\n\n"
        else:
            out += f"<ansicyan><b>AI:</b></ansicyan> {m['content']}\n\n"
    return HTML(out)


# -------------------------------
# 5. Tool Logs Pane
# -------------------------------
def get_tool_text():
    if not state.tool_logs:
        return HTML("<i>No tool calls yet</i>")
    return HTML("\n".join(state.tool_logs[-10:]))


# -------------------------------
# 6. Bottom Toolbar
# -------------------------------
def get_toolbar_text():
    return HTML(
        f" <b>Agent:</b> {state.agent['name']} "
        f"| <b>Msgs:</b> {len(state.messages)} "
        f"| <b>F1</b> Help "
        f"| <b>F2</b> Save "
        f"| <b>F3</b> Switch Agent "
        f"| <b>F10</b> Quit"
    )


# -------------------------------
# 7. Input Area
# -------------------------------
input_field = TextArea(
    height=3,
    prompt="> ",
    multiline=False,
    wrap_lines=True,
)


# -------------------------------
# 8. Layout
# -------------------------------
sidebar = Frame(
    Window(FormattedTextControl(get_sidebar_text), width=28),
    title="Sidebar",
    style="class:sidebar",
)

chat_pane = Frame(
    Window(FormattedTextControl(get_chat_text), wrap_lines=True),
    title="Chat",
    style="class:chat",
)

tool_pane = Frame(
    Window(FormattedTextControl(get_tool_text), height=8, wrap_lines=True),
    title="Tools",
    style="class:tools",
)

toolbar = Window(
    FormattedTextControl(get_toolbar_text),
    height=1,
    style="class:toolbar",
)

right_side = HSplit([chat_pane, tool_pane, input_field])
body = VSplit([sidebar, right_side])
root = HSplit([body, toolbar])


# -------------------------------
# 9. Key Bindings
# -------------------------------
kb = KeyBindings()


@kb.add("f10")
def _(event):
    event.app.exit()


@kb.add("f1")
def _(event):
    state.tool_logs.append("Help: Type message + Enter | F2 Save | F3 Switch | F10 Quit")


@kb.add("f2")
def _(event):
    sid = save_session(state.messages, state.agent["name"])
    state.tool_logs.append(f"Saved session: {sid}")


@kb.add("f3")
def _(event):
    agents = list_agents() or ["default"]
    current = state.agent["name"]
    if current in agents:
        idx = (agents.index(current) + 1) % len(agents)
    else:
        idx = 0
    state.agent = load_agent(agents[idx])
    state.tool_logs.append(f"Switched to agent: {state.agent['name']}")


@kb.add("enter")
def _(event):
    text = input_field.text.strip()
    if not text:
        return
    input_field.text = ""

    state.messages.append({"role": "user", "content": text})
    state.tool_logs.append(f"Calling {state.agent['name']}...")

    result = state.graph.invoke({
        "user_input": text,
        "messages": state.messages,
        "system_prompt": state.agent.get("system_prompt", ""),
        "permissions": state.agent.get("permissions", []),
        "agent_name": state.agent["name"],
    })

    answer = result.get("answer", "")
    state.messages.append({"role": "assistant", "content": answer})
    state.tool_logs.append("Response received")


# -------------------------------
# 10. Build Application
# -------------------------------
app = Application(
    layout=Layout(root, focused_element=input_field),
    key_bindings=kb,
    style=style,
    full_screen=True,
    mouse_support=True,
    refresh_interval=0.4,
)


def run_tui():
    app.run()
