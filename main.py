import os
import logging

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# ===== ENV (Railway Variables) =====
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
PUBLIC_URL = os.getenv("PUBLIC_URL", "").strip().rstrip("/")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing in Railway Variables")
if not PUBLIC_URL.startswith("https://"):
    raise RuntimeError("PUBLIC_URL must start with https:// (example: https://xxxx.up.railway.app)")
if not ADMIN_CHAT_ID.isdigit():
    raise RuntimeError("ADMIN_CHAT_ID must be a number (Telegram numeric ID)")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

# ===== FastAPI + Telegram App =====
api = FastAPI()
tg_app = Application.builder().token(BOT_TOKEN).build()

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running on Railway!\nSend /start to test.")

tg_app.add_handler(CommandHandler("start", start))


# ===== Startup: init + webhook set =====
@api.on_event("startup")
async def on_startup():
    await tg_app.initialize()
    await tg_app.bot.set_webhook(url=f"{PUBLIC_URL}/webhook")
    await tg_app.start()
    logging.info("✅ Webhook set to: %s/webhook", PUBLIC_URL)

@api.on_event("shutdown")
async def on_shutdown():
    await tg_app.stop()
    await tg_app.shutdown()


@api.get("/")
def home():
    return {"status": "running"}


@api.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}
api = FastAPI()

@api.get("/")
def home():
    return {"status": "running"}
