# 🐱 longcat-sgpt

A lightweight **Shell GPT** CLI tool powered by [LongCat AI](https://longcat.chat) — ask questions, generate shell commands, explain code, and more, all from your terminal.

```bash
sgpt "what is a segfault?"
sgpt --shell "find all log files larger than 10MB"
cat error.log | sgpt "what is wrong here?"
git diff | sgpt "summarize these changes"
```

---

## ✨ Features

- 💬 **Ask anything** from your terminal
- 🐚 **Shell mode** — get raw commands, no fluff
- 🧠 **Thinking mode** — deep reasoning for hard problems
- 💻 **Code mode** — get clean code output
- 📖 **Explain mode** — step-by-step explanations
- 📋 **Pipe support** — pipe any file/output into it
- ⚡ **Streaming** — responses appear word by word
- 🔑 **Key management** — store your API key in config

---

## 📦 Installation

### Option 1 — Install directly from GitHub (recommended)

```bash
pip install git+https://github.com/t4threats/longcat-sgpt
```

### Option 2 — Clone and install locally

```bash
git clone https://github.com/t4threats/longcat-sgpt
cd longcat-sgpt
pip install -e .
```

---

## 🔑 Setup

### Step 1 — Get your LongCat API key

1. Go to [longcat.chat/platform](https://longcat.chat/platform)
2. Register / log in
3. Click **API Keys** → **Create API Key**

### Step 2 — Save your key (pick one method)

**Method A — Save to config file (permanent):**
```bash
sgpt --set-key YOUR_API_KEY_HERE
```

**Method B — Environment variable (session or permanent):**
```bash
# Temporary (current session only)
export LONGCAT_API_KEY=your_key_here

# Permanent — add this line to your ~/.bashrc or ~/.zshrc
echo 'export LONGCAT_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

---

## 🚀 Usage

### Basic question
```bash
sgpt "explain what docker volumes are"
```

### Shell command mode
Returns only the raw shell command — ready to copy/paste or pipe to `bash`:
```bash
sgpt --shell "compress all jpg files in current folder"
# Output: find . -name "*.jpg" | xargs zip images.zip
```

### Code mode
```bash
sgpt --code "python function to read a CSV and return a list of dicts"
```

### Explain mode
```bash
sgpt --explain "what is a race condition?"
```

### Deep thinking mode
For math, logic, or complex reasoning:
```bash
sgpt --model think "what is the time complexity of quicksort and why?"
```

### Pipe mode
Feed any file or command output into sgpt:
```bash
# Explain an error log
cat error.log | sgpt "what is causing this error?"

# Summarize a file
cat README.md | sgpt "give me a 3 bullet summary"

# Understand a git diff
git diff | sgpt "explain what changed"

# Analyze command output
ps aux | sgpt "which process is using the most memory?"

# Combined: question + piped content
cat config.yaml | sgpt "is there anything wrong with this config?"
```

---

## 🤖 Available Models

| Flag | Model | Best For |
|------|-------|----------|
| `--model chat` | LongCat-Flash-Chat | General use (default) |
| `--model think` | LongCat-Flash-Thinking-2601 | Hard reasoning & math |
| `--model lite` | LongCat-Flash-Lite | Fastest responses |

```bash
# Set a permanent default model
sgpt --set-model think
```

---

## ⚙️ Config Commands

```bash
sgpt --set-key YOUR_KEY     # Save API key
sgpt --set-model think      # Set default model
sgpt --show-config          # View current settings
sgpt --models               # List all available models
sgpt --version              # Show version
```

---

## 📁 Project Structure

```
longcat-sgpt/
├── sgpt/
│   ├── __init__.py       # Package version
│   └── main.py           # All CLI logic
├── pyproject.toml        # Package config (pip install)
├── .env.example          # Template for your API key
├── .gitignore            # Keeps secrets out of git
├── LICENSE               # MIT
└── README.md             # This file
```

---

## 🔒 Security Note

**Never commit your API key to GitHub.**
- Use `sgpt --set-key` to store it locally in `~/.config/longcat-sgpt/config.json`
- Or use an environment variable
- The `.gitignore` already excludes `.env` files

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 🙏 Credits

- Powered by [LongCat AI](https://longcat.ai) by Meituan
- Inspired by [shell-gpt](https://github.com/TheR1D/shell_gpt)
