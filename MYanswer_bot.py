import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ---------------- بارگذاری متغیرها از .env ----------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")

# ---------------- تنظیمات لاگ ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ---------------- مراحل کانورسیشن ----------------
ROLE_INPUT = 1

# ---------------- فرمان /start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("تعیین نقش", callback_data='set_role')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من با هوش مصنوعی DeepSeek کار می‌کنم.\n"
        "روی دکمه زیر کلیک کن تا نقش هوش مصنوعی رو تعیین کنی.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'set_role':
        await query.edit_message_text("لطفا نقش ربات (Prompt) را وارد کن:")
        return ROLE_INPUT

async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role_text = update.message.text
    context.user_data['role_prompt'] = role_text
    await update.message.reply_text(
        f"نقش شما ذخیره شد: {role_text}\n"
        "حال هر پیامی بفرستی، ربات با این نقش جواب می‌دهد."
    )
    return ConversationHandler.END

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    role_prompt = context.user_data.get('role_prompt', '')

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"]
    except Exception:
        bot_reply = "متاسفم، مشکلی در ارتباط با دیپ‌سیک پیش آمد."

    await update.message.reply_text(bot_reply)

# ---------------- اجرای بات ----------------
def main():
    # JobQueue به صورت خودکار توسط ApplicationBuilder مدیریت می‌شود
    app = ApplicationBuilder() \
        .token(TELEGRAM_TOKEN) \
        .build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={ROLE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_role)]},
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("ربات با موفقیت راه‌اندازی شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
