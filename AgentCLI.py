#!/usr/bin/env python3
"""
agent.py — a professional terminal AI agent client.

Works against any OpenAI-compatible /chat/completions endpoint, or
Anthropic's /v1/messages endpoint.


"""

import argparse
import json
import os
import sys
import textwrap

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme
from rich.align import Align
from rich.text import Text

# =====================================================================

# =====================================================================
BASE_URL = "https://nexusapi.navigatelabs.ai"      
API_KEY = ""       
MODEL = "gpt-4.1-nano"   # <-- change to whichever model your key can access
FORMAT = "openai"        # "openai" or "anthropic"

# =====================================================================

# =====================================================================


# ---------------------------------------------------------------------------
# Aesthetic: a soft, professional pastel palette on a dark background.
# ---------------------------------------------------------------------------
THEME = Theme({
    "accent": "bold #A7C7E7",      # pastel blue
    "accent2": "bold #C9B6E4",     # pastel lavender
    "mint": "#B5EAD7",             # pastel mint
    "peach": "#FFDAC1",            # pastel peach
    "dim": "grey62",
    "user": "bold #A7C7E7",
    "agent": "bold #C9B6E4",
    "error": "bold #FFB3B3",
    "border": "#8FA6C4",
})
console = Console(theme=THEME)


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

class AgentError(Exception):
    pass


def call_openai(base_url: str, api_key: str, model: str, messages: list) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    try:
        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={"model": model, "messages": messages},
            timeout=60,
        )
    except requests.RequestException as e:
        raise AgentError(f"Connection failed: {e}") from e

    if not resp.ok:
        raise AgentError(f"HTTP {resp.status_code}: {resp.text[:400]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"] or "(empty response)"
    except (KeyError, IndexError):
        raise AgentError(f"Unexpected response shape: {json.dumps(data)[:400]}")


def call_anthropic(base_url: str, api_key: str, model: str, messages: list) -> str:
    url = base_url.rstrip("/") + "/v1/messages"
    try:
        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={"model": model, "max_tokens": 1024, "messages": messages},
            timeout=60,
        )
    except requests.RequestException as e:
        raise AgentError(f"Connection failed: {e}") from e

    if not resp.ok:
        raise AgentError(f"HTTP {resp.status_code}: {resp.text[:400]}")

    data = resp.json()
    try:
        blocks = data.get("content", [])
        return "\n".join(b.get("text", "") for b in blocks) or "(empty response)"
    except (KeyError, IndexError):
        raise AgentError(f"Unexpected response shape: {json.dumps(data)[:400]}")


CALLERS = {
    "openai": call_openai,
    "anthropic": call_anthropic,
}


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

def print_banner(model: str, fmt: str):
    title = Text("AI AGENT", style="bold #A7C7E7", justify="center")
    subtitle = Text(f"{fmt}  ·  {model}", style="dim", justify="center")
    body = Text.assemble(title, "\n", subtitle)
    console.print()
    console.print(
        Panel(
            Align.center(body),
            border_style="border",
            padding=(1, 4),
            expand=False,
        ),
        justify="center",
    )
    console.print(
        Align.center(Text("type your message  ·  /reset clears history  ·  /exit quits", style="dim"))
    )
    console.print()


def print_message(role: str, text: str):
    if role == "user":
        console.print(Panel(text, title="[user]you[/user]", border_style="accent",
                             title_align="left", padding=(0, 1)))
    elif role == "assistant":
        console.print(Panel(Markdown(text), title="[agent]agent[/agent]", border_style="accent2",
                             title_align="left", padding=(0, 1)))
    elif role == "error":
        console.print(Panel(text, title="[error]error[/error]", border_style="error",
                             title_align="left", padding=(0, 1)))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def get_config(args) -> dict:
    base_url = args.base_url or os.environ.get("AGENT_BASE_URL") or BASE_URL
    api_key = args.api_key or os.environ.get("AGENT_API_KEY") or API_KEY
    model = args.model or os.environ.get("AGENT_MODEL") or MODEL
    fmt = args.format or os.environ.get("AGENT_FORMAT") or FORMAT

    if not base_url:
        base_url = Prompt.ask("[dim]Base URL[/dim]")
    if not api_key:
        api_key = Prompt.ask("[dim]API key[/dim]", password=True)
    if not model:
        model = Prompt.ask("[dim]Model[/dim]")
    if fmt not in CALLERS:
        fmt = Prompt.ask("[dim]Format[/dim]", choices=list(CALLERS.keys()), default="openai")

    return {"base_url": base_url, "api_key": api_key, "model": model, "format": fmt}


def chat_loop(config: dict):
    caller = CALLERS[config["format"]]
    history = []

    while True:
        console.print()
        try:
            user_input = Prompt.ask("[user]›[/user]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]goodbye[/dim]")
            break

        if not user_input.strip():
            continue

        if user_input.strip() in ("/exit", "/quit"):
            console.print("[dim]goodbye[/dim]")
            break

        if user_input.strip() == "/reset":
            history.clear()
            console.print("[dim]history cleared[/dim]")
            continue

        history.append({"role": "user", "content": user_input})

        with console.status("[dim]thinking…[/dim]", spinner="dots"):
            try:
                reply = caller(
                    config["base_url"], config["api_key"], config["model"], history
                )
            except AgentError as e:
                print_message("error", str(e))
                history.pop()  # don't keep a failed turn in context
                continue

        history.append({"role": "assistant", "content": reply})
        print_message("assistant", reply)


def main():
    parser = argparse.ArgumentParser(description="Professional terminal AI agent client.")
    parser.add_argument("--base-url", help="API base URL")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="Model name")
    parser.add_argument(
        "--format", choices=list(CALLERS.keys()), help="API format (default: openai)"
    )
    args = parser.parse_known_args()[0]

    config = get_config(args)
    print_banner(config["model"], config["format"])
    try:
        chat_loop(config)
    except KeyboardInterrupt:
        console.print("\n[dim]goodbye[/dim]")
        sys.exit(0)


if __name__ == "__main__":
    main()