import os
import logging
from flask import Flask, request
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Логирование
logging.basicConfig(level=logging.INFO)

# Настройки Telegram
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Настройки Google Sheets
GOOGLE_SHEET_KEY = os.getenv("GOOGLE_SHEET_KEY")
GOOGLE_CREDENTIALS_JSON = "google_credentials.json"

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_KEY).sheet1

# Flask-приложение для webhook
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Команда /start
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я бот для бронирования. Напиши дату и время.")

# Обработка бронирования
@bot.message_handler(func=lambda m: True)
def handle_booking(message):
    try:
        # Пример формата: "13.08.2025 10:00"
        booking_time = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")

        # Проверка занятости
        data = sheet.get_all_records()
        for row in data:
            if row["Дата"] == booking_time.strftime("%d.%m.%Y") and row["Время"] == booking_time.strftime("%H:%M"):
                bot.send_message(message.chat.id, "Это время уже занято. Выберите другое.")
                return
        
        # Запись в Google Sheet
        sheet.append_row([booking_time.strftime("%d.%m.%Y"), booking_time.strftime("%H:%M"), message.chat.username])
        bot.send_message(message.chat.id, "Запись подтверждена ✅")
    
    except ValueError:
        bot.send_message(message.chat.id, "Введите дату и время в формате: 13.08.2025 10:00")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    app.run(host="0.0.0.0", port=port)
