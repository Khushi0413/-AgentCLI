🤖 AgentCLI

A clean, minimal terminal client that lets you chat with any OpenAI-compatible or Anthropic-compatible AI API — 


## ✨ Features

- 🔌 **Dual API support** — works with OpenAI-format `/chat/completions` endpoints or Anthropic's `/v1/messages` endpoint
- 💬 **Persistent session history** — keeps the conversation in context until you reset or exit
- ⚙️ **Flexible config** — set credentials via CLI flags, environment variables, in-file defaults, or interactive prompt
- 🧹 **`/reset`** — clear conversation history mid-session
- 🚪 **`/exit` / `/quit`** — end the session cleanly (also handles Ctrl+C / Ctrl+D)
- 🛟 **Graceful error handling** — failed turns are dropped from history so they aren't resent

## 🖥️ Demo

> Add a terminal recording or screenshot here (e.g. asciinema, Carbon, or a GIF)

## 🛠️ Tech Stack

- **Python 3.8+** — core language
- **[Rich](https://github.com/Textualize/rich)** — terminal UI (panels, markdown rendering, prompts, spinners)
- **[Requests](https://docs.python-requests.org/)** — HTTP calls to the chat API
- **argparse** — CLI flag parsing

## 🚀 Getting Started

```bash
pip install requests rich
python agent.py
```

### Configuration (priority order)

1. **CLI flags**: `--base-url`, `--api-key`, `--model`, `--format`
2. **Environment variables**: `AGENT_BASE_URL`, `AGENT_API_KEY`, `AGENT_MODEL`, `AGENT_FORMAT`
3. **In-file defaults**: edit the block near the top of `agent.py`
4. **Interactive prompt**: anything still missing is asked for at runtime (API key input is masked)

```bash
python agent.py --base-url https://api.openai.com/v1 --api-key sk-... --model gpt-4o --format openai
```

> ⚠️ Don't commit real API keys — use environment variables or CLI flags instead of hardcoding secrets in `agent.py`.

## ⌨️ Commands

| Command | Effect |
|---|---|
| `/reset` | Clear conversation history |
| `/exit`, `/quit` | End the session |
| `Ctrl+C` / `Ctrl+D` | Exit gracefully |

## 📦 Project Structure

```
agent.py   # config, API callers, UI, and chat loop — all in one file
```

## 📝 Notes

- Requests time out after 60 seconds
- `--format` must be `openai` or `anthropic`; anything else triggers an interactive prompt
