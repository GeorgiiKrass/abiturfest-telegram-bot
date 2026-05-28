import os
import json
from datetime import datetime

import gspread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from google.oauth2.service_account import Credentials


BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME")
GOOGLE_CREDENTIALS_RAW = os.getenv("GOOGLE_CREDENTIALS")

google_credentials = json.loads(GOOGLE_CREDENTIALS_RAW)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_sheet():
    credentials = Credentials.from_service_account_info(
        google_credentials,
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open(SHEET_NAME)

    return spreadsheet.sheet1


def save_user(user):
    sheet = get_sheet()

    telegram_id = str(user.id)
    existing_ids = sheet.col_values(2)

    if telegram_id in existing_ids:
        print("User already exists in Google Sheet")
        return

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        telegram_id,
        user.username or "",
        user.first_name or "",
        user.last_name or ""
    ])

    print("User saved to Google Sheet")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    print(f"START pressed: {user.id} @{user.username}")

    try:
        save_user(user)
    except Exception as e:
        print(f"GOOGLE SHEET ERROR: {e}")

    text = """
Вас вітає бот вступної кампанії Фахового коледжу вимірювань 🎓✨

Тут ви можете:
⚡️ дізнатись про спеціальності
⚡️ переглянути умови вступу
⚡️ отримати консультацію
⚡️ дізнатись про студентське життя
⚡️ знайти відповіді на популярні питання

📍 Одеса, вул. Спиридонівська, 13

Обирай сучасну освіту та свій майбутній фах разом із ФКВ 🙌
"""

    keyboard = [
        [InlineKeyboardButton("📍 Відкрити на мапі", url="https://maps.app.goo.gl/ki4TLBQWUZUTQvLa7")],
        [InlineKeyboardButton("🌐 Сайт коледжу", url="https://okv.suitt.edu.ua/")],
        [InlineKeyboardButton("💬 Приймальна комісія / Вступ", url="https://t.me/vspfahovykollegevimiryvan")],
        [InlineKeyboardButton("📝 Реєстрація — анкета вступника 2026", url="https://docs.google.com/forms/d/e/1FAIpQLSeWyvm3NW9rHNLFeMPYXOYq4AbHXHLP473zlz9UEqrHUTIw_Q/viewform?usp=dialog")],
        [
            InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/fkv.official?igsh=OHdic3R4bXhrbWtj"),
            InlineKeyboardButton("👍 Facebook", url="https://www.facebook.com/share/g/1GeDiHhk4E/?mibextid=wwXIfr")
        ],
        [InlineKeyboardButton("🎵 TikTok", url="https://www.tiktok.com/@fkv.official?_r=1&_t=ZS-94eLCwGqXWZ")],
        [InlineKeyboardButton("📚 Реєстрація на підготовчі курси", url="https://docs.google.com/forms/d/e/1FAIpQLSft7bZfjHB7Fmg7rKDUp5BIjcQqJoH5feMeVftLf58CAEiJFw/viewform?usp=dialog")]
    ]

    try:
        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        print("Telegram message sent")
    except Exception as e:
        print(f"TELEGRAM SEND ERROR: {e}")


def main():
    print("Bot starting...")

    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is missing")

    if not SHEET_NAME:
        print("ERROR: SHEET_NAME is missing")

    if not GOOGLE_CREDENTIALS_RAW:
        print("ERROR: GOOGLE_CREDENTIALS is missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
