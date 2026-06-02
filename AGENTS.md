# 🤖 AI Agent Developer Guide (AGENTS.md)

Welcome! You are an AI Developer Agent (Codex, ChatGPT, Claude, or any LLM) tasked with maintaining, updating, and improving this **Discord Auto-Seller Bot**.
Your goal is to fully automate the development, bug fixing, and feature deployment process.

---

## 🛠️ System Architecture & Workflow

```
[Your Chat Interface] 
       │ (Edits code via GitHub API / TypingMind Integration)
       ▼
[GitHub Repository] (njh2008/discord-auto-seller-bot)
       │ (Automatic Webhook Trigger)
       ▼
[Railway Hosting] (Auto-builds & deploys bot.py)
       │ (24/7 Active Bot)
       ▼
[Discord Server] (Immediate live updates!)
```

---

## 📂 Project Structure

*   `bot.py`: The main entry point of the Discord Bot. Contains all commands, event listeners, and business logic.
*   `database.json`: Local JSON database storing inventory, orders, user balances, and gacha settings.
*   `requirements.txt`: Python dependencies.
*   `AGENTS.md`: This instruction manual (Do not modify unless optimizing agent instructions).

---

## 💾 Zero-Database Persistence Strategy (Discord-as-a-DB Backup)

Since **Railway** has an ephemeral filesystem (it resets every time the bot redeploys or restarts), any local `database.json` changes would normally be lost.
To solve this without requiring a paid database, this bot implements a **Discord Backup System**:
1.  Every time the database is modified, it is serialized to JSON and sent as a backup file to a private **Discord Log Channel** (configured via `BACKUP_CHANNEL_ID`).
2.  When the bot starts up, it automatically fetches the latest message from the backup channel, downloads the JSON file, and restores the database.
3.  **Rule for AI Agents**: If you modify the database structure, ensure you update the serialization/deserialization logic in `bot.py` accordingly.

---

## ⚙️ How to Modify and Deploy Code

When the user asks you to add a feature, fix a bug, or change settings:

1.  **Analyze**: Read `bot.py` and understand the current implementation.
2.  **Write Code**: Write clean, robust, and fully-featured Python code. Avoid placeholders or truncated code blocks.
3.  **Commit directly to `main` branch**:
    *   If you are running in **TypingMind** with GitHub Integration enabled, use the GitHub tool to overwrite `bot.py` (and `requirements.txt` if you added new libraries) and commit directly.
    *   If you do not have direct write access, provide the complete, updated file and instruct the user to copy-paste it into GitHub or use GitHub Web Editor.
4.  **Verify**: Railway will automatically detect the commit, build, and redeploy the bot within 1-2 minutes.

---

## 📋 Coding Rules & Guidelines

1.  **Never Use Ephemeral Variables for State**: All state (stock, users, orders, gacha config) must be saved in the `db` dictionary and synchronized using `save_db()`.
2.  **Error Handling**: Wrap Discord commands and API calls in `try-except` blocks to prevent the bot from crashing.
3.  **Discord.py v2+ Syntax**: Use modern `discord.ext.commands` or Slash Commands.
4.  **Security**: Never hardcode tokens or sensitive keys. Use `os.getenv('DISCORD_TOKEN')` and other environment variables.
