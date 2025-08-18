import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------- بارگذاری متغیرها از .env ----------------
load_dotenv()  # فایل .env رو لود می‌کنه

TELEGRAM_TOKEN = "8258764176:AAGUJIsImGOm53lDuvG18-O2MmECKRAFy9o"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")

# فعال کردن لاگ برای دیباگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

# ---------------- توابع ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من با هوش مصنوعی DeepSeek کار می‌کنم. هرچی می‌خوای بپرس 🙂")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
    data = response.json()

    try:
        bot_reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        bot_reply = "متاسفم، مشکلی در ارتباط با دیپ‌سیک پیش اومد."

    await update.message.reply_text(bot_reply)

# ---------------- اجرای بات ----------------
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("ربات با DeepSeek روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
