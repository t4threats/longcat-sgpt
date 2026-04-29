#!/usr/bin/env python3
"""
longcat-sgpt: A Shell GPT powered by LongCat AI (by Meituan)
Usage:
    sgpt "your question here"
    sgpt --shell "list all python files recursively"
    sgpt --model think "hard reasoning problem"
    cat file.txt | sgpt "summarize this"
    cat error.log | sgpt "what is wrong here?"
"""

import sys
import os
import argparse
import json

# ─────────────────────────────────────────────
# Config & Constants
# ─────────────────────────────────────────────

LONGCAT_BASE_URL = "https://api.longcat.chat/openai/v1"
CONFIG_DIR = os.path.expanduser("~/.config/longcat-sgpt")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

MODELS = {
    "chat":  "LongCat-Flash-Chat",           # Fast, general purpose (default)
    "think": "LongCat-Flash-Thinking-2601",  # Deep reasoning, slower
    "lite":  "LongCat-Flash-Lite",           # Lightest, fastest
}

SYSTEM_PROMPTS = {
    "default": (
        "You are a helpful, concise terminal assistant. "
        "Give direct answers. Avoid unnecessary padding."
    ),
    "shell": (
        "You are a shell command expert. "
        "When asked to do something, respond ONLY with the exact shell command. "
        "No explanation, no markdown, no backticks, no commentary — just the raw command."
    ),
    "code": (
        "You are an expert programmer. "
        "Output only clean, working code with minimal inline comments. "
        "No markdown fences unless specifically asked."
    ),
    "explain": (
        "You are a patient teacher. Explain things step by step in simple terms. "
        "Use examples where helpful."
    ),
}


# ─────────────────────────────────────────────
# Config helpers
# ─────────────────────────────────────────────

def load_config():
    """Load saved config (API key, default model, etc.)"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(data: dict):
    """Persist config to ~/.config/longcat-sgpt/config.json"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Config saved to {CONFIG_FILE}")


def get_api_key():
    """
    API key priority:
    1. Environment variable LONGCAT_API_KEY
    2. Saved config file
    """
    key = os.environ.get("LONGCAT_API_KEY")
    if key:
        return key
    config = load_config()
    key = config.get("api_key")
    if key:
        return key
    print("❌ No API key found.")
    print("Set it with:  sgpt --set-key YOUR_KEY")
    print("Or export:    export LONGCAT_API_KEY=YOUR_KEY")
    sys.exit(1)


# ─────────────────────────────────────────────
# Core query function
# ─────────────────────────────────────────────

def query(prompt: str, model_alias: str = "chat", mode: str = "default"):
    """
    Send a prompt to LongCat API and stream the response to stdout.

    Args:
        prompt:      The user's question or instruction
        model_alias: One of 'chat', 'think', 'lite'
        mode:        One of 'default', 'shell', 'code', 'explain'
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ Missing dependency. Run:  pip install openai")
        sys.exit(1)

    api_key = get_api_key()
    model_name = MODELS.get(model_alias, MODELS["chat"])
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])

    client = OpenAI(api_key=api_key, base_url=LONGCAT_BASE_URL)

    try:
        stream = client.chat.completions.create(
            model=model_name,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt},
            ],
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
        print()  # newline after response

    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            print("❌ Invalid API key. Check your key and try again.")
        elif "429" in err:
            print("❌ Rate limit hit. Wait a moment and retry.")
        elif "Connection" in err:
            print("❌ Cannot reach LongCat API. Check your internet connection.")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="sgpt",
        description="🐱 Shell GPT powered by LongCat AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sgpt "what is a segfault?"
  sgpt --shell "find all .log files larger than 10MB"
  sgpt --model think "explain the travelling salesman problem"
  sgpt --code "write a python function to parse JSON safely"
  cat error.log | sgpt "what is wrong here?"
  ls -la | sgpt "which file is largest?"
  git diff | sgpt "summarize these changes"
        """,
    )

    # The actual prompt words (can be empty if piping)
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Your question or instruction",
    )

    # Model selection
    parser.add_argument(
        "-m", "--model",
        default=None,
        choices=list(MODELS.keys()),
        help="Model: chat (default), think (reasoning), lite (fastest)",
    )

    # Mode flags (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-s", "--shell",
        action="store_true",
        help="Return only a shell command (no explanation)",
    )
    mode_group.add_argument(
        "-c", "--code",
        action="store_true",
        help="Return only code output",
    )
    mode_group.add_argument(
        "-e", "--explain",
        action="store_true",
        help="Get a step-by-step explanation",
    )

    # Config commands
    parser.add_argument(
        "--set-key",
        metavar="API_KEY",
        help="Save your LongCat API key to config",
    )
    parser.add_argument(
        "--set-model",
        choices=list(MODELS.keys()),
        help="Set your default model",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current config",
    )
    parser.add_argument(
        "--models",
        action="store_true",
        help="List available models",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version",
    )

    args = parser.parse_args()

    # ── Handle utility commands first ──

    if args.version:
        from sgpt import __version__
        print(f"longcat-sgpt v{__version__}")
        return

    if args.models:
        print("\n🐱 Available LongCat Models:\n")
        for alias, name in MODELS.items():
            tag = " ← default" if alias == "chat" else ""
            print(f"  --model {alias:<8}  {name}{tag}")
        print()
        return

    if args.set_key:
        config = load_config()
        config["api_key"] = args.set_key
        save_config(config)
        print("🔑 API key saved. You're ready to use sgpt!")
        return

    if args.set_model:
        config = load_config()
        config["default_model"] = args.set_model
        save_config(config)
        print(f"✅ Default model set to: {args.set_model} ({MODELS[args.set_model]})")
        return

    if args.show_config:
        config = load_config()
        if not config:
            print("No config saved yet.")
        else:
            key = config.get("api_key", "")
            masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "not set"
            print(f"API Key:       {masked}")
            print(f"Default Model: {config.get('default_model', 'chat')}")
        return

    # ── Build the prompt ──

    # Grab piped stdin (e.g. cat file.txt | sgpt "summarize")
    piped_input = ""
    if not sys.stdin.isatty():
        piped_input = sys.stdin.read().strip()

    prompt_words = " ".join(args.prompt).strip()

    if piped_input and prompt_words:
        full_prompt = f"{prompt_words}\n\n---\n{piped_input}"
    elif piped_input:
        full_prompt = piped_input
    else:
        full_prompt = prompt_words

    if not full_prompt:
        parser.print_help()
        sys.exit(0)

    # ── Pick model ──
    config = load_config()
    model = args.model or config.get("default_model", "chat")

    # ── Pick mode ──
    if args.shell:
        mode = "shell"
    elif args.code:
        mode = "code"
    elif args.explain:
        mode = "explain"
    else:
        mode = "default"

    # ── Run! ──
    query(full_prompt, model_alias=model, mode=mode)


if __name__ == "__main__":
    main()
