#!/usr/bin/env python3
"""Amily AI Telegram Bot -- DeepSeek V4 Pro via OpenRouter."""

import os
import json
import logging
from pathlib import Path

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode, ChatAction

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("amily-telegram")

# --- Config ---
ENV_FILE = Path(os.environ.get("ENV_FILE", "/home/amily/.config/telegram/.env"))
OWNER_FILE = Path("/home/amily/.config/telegram/owner.json")
MAX_HISTORY = 20  # conversation turns to keep per chat
SYSTEM_PROMPT = (
    "You are Amily AI, Anthony Nguyen's personal AI assistant. "
    "You are helpful, concise, and technically strong. "
    "Format responses using Telegram MarkdownV2 conventions: "
    "use backticks for inline code, triple backticks for code blocks, "
    "and keep responses scannable with bullet points. "
    "You are powered by DeepSeek V4 Pro."
)


def load_env():
    """Load environment variables from .env file."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


load_env()

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENROUTER_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek/deepseek-v4-pro")

# --- Owner lock ---
_owner_id: int | None = None


def get_owner_id() -> int | None:
    global _owner_id
    if _owner_id is not None:
        return _owner_id
    if OWNER_FILE.exists():
        data = json.loads(OWNER_FILE.read_text())
        _owner_id = data.get("owner_id")
    return _owner_id


def set_owner_id(user_id: int):
    global _owner_id
    _owner_id = user_id
    OWNER_FILE.parent.mkdir(parents=True, exist_ok=True)
    OWNER_FILE.write_text(json.dumps({"owner_id": user_id}))
    logger.info("Owner locked to user_id=%d", user_id)


def is_owner(user_id: int) -> bool:
    owner = get_owner_id()
    if owner is None:
        return True  # first user claims ownership
    return user_id == owner


# --- Conversation history ---
conversations: dict[int, list[dict]] = {}


def get_history(chat_id: int) -> list[dict]:
    return conversations.setdefault(chat_id, [])


def add_message(chat_id: int, role: str, content: str):
    history = get_history(chat_id)
    history.append({"role": role, "content": content})
    # trim to max history
    if len(history) > MAX_HISTORY * 2:
        conversations[chat_id] = history[-(MAX_HISTORY * 2):]


# --- OpenRouter API ---
async def call_deepseek(chat_id: int, user_message: str) -> str:
    add_message(chat_id, "user", user_message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_history(chat_id)

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://amily.ai",
                "X-Title": "Amily AI Telegram Bot",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    reply = data["choices"][0]["message"]["content"]
    add_message(chat_id, "assistant", reply)
    return reply


# --- Telegram escape for MarkdownV2 ---
SPECIAL_CHARS = r"_[]()~`>#+-=|{}.!"


def escape_md(text: str) -> str:
    """Escape special chars for Telegram MarkdownV2, preserving code blocks."""
    parts = []
    segments = text.split("```")
    for i, seg in enumerate(segments):
        if i % 2 == 1:
            # inside code block -- don't escape
            parts.append(f"```{seg}```")
        else:
            # outside code block -- escape, but preserve inline code
            inline_parts = seg.split("`")
            for j, ip in enumerate(inline_parts):
                if j % 2 == 1:
                    parts.append(f"`{ip}`")
                else:
                    for ch in SPECIAL_CHARS:
                        ip = ip.replace(ch, f"\\{ch}")
                    parts.append(ip)
    return "".join(parts)


# --- Handlers ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        await update.message.reply_text("Access denied.")
        return

    # claim ownership on first interaction
    if get_owner_id() is None:
        set_owner_id(user.id)

    await update.message.reply_text(
        f"Hey Anthony! Amily AI is online.\n"
        f"Model: {MODEL}\n"
        f"Send me anything to chat.",
    )


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    chat_id = update.effective_chat.id
    conversations.pop(chat_id, None)
    await update.message.reply_text("Conversation cleared.")


async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(f"Current model: {MODEL}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        # claim ownership if no owner set yet
        if get_owner_id() is None:
            set_owner_id(user.id)
        else:
            return  # silently ignore non-owner messages

    chat_id = update.effective_chat.id
    user_text = update.message.text

    # show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        reply = await call_deepseek(chat_id, user_text)

        # try sending with MarkdownV2 first, fall back to plain text
        try:
            escaped = escape_md(reply)
            await update.message.reply_text(escaped, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception:
            # fallback: try regular Markdown
            try:
                await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                # final fallback: plain text
                await update.message.reply_text(reply)

    except httpx.HTTPStatusError as e:
        logger.error("OpenRouter API error: %s", e.response.text)
        await update.message.reply_text(
            f"API error ({e.response.status_code}). Check logs."
        )
    except Exception as e:
        logger.exception("Unexpected error")
        await update.message.reply_text(f"Error: {type(e).__name__}: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled exception:", exc_info=context.error)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("model", model_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Starting Amily AI Telegram bot (model=%s)", MODEL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
