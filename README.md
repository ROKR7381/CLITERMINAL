# MyAgent - OpenCode-style AI Agent CLI

A powerful terminal AI agent CLI built with LangGraph + OpenAI.

## Features

- Multi-agent registry (YAML-based)
- Tool permissions (read/write/shell/search)
- Session save/load
- Streaming markdown rendering
- Token + cost tracking
- Full-screen TUI mode
- Project context scanning

## Install

```bash
pip install myagent
```

## Usage

```bash
# Interactive mode
myagent

# TUI mode
myagent tui

# One-shot mode
myagent run "Explain LangGraph"
```

## Commands

| Command | Description |
|---------|-------------|
| `/init` | Scan project & build AGENTS.md |
| `/help` | Show help |
| `/exit` | Exit CLI |
| `/save` | Save session |
| `/load <id>` | Load session |
| `/agents` | List agents |
| `/agent use <name>` | Switch agent |
| `/tools` | Show available tools |
| `/read <path>` | Read file |
| `/write <path> <txt>` | Write file |
| `/ls <path>` | List directory |
| `/shell <cmd>` | Run shell command |
| `/search <path> <kw>` | Search in files |
| `/clear` | Clear messages |

## TUI Keys

| Key | Action |
|-----|--------|
| F1 | Help |
| F2 | Save session |
| F3 | Switch agent |
| F10 | Quit |

## License

MIT
