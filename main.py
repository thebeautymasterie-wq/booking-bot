import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("8481237197:AAFYLmYXPoTjTKWg4NJNDqzQLlIB_j9aqnE")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для записи в Beauty Studio 💅")

bot_app.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "OK", 200

# Главная страница для проверки
@app.route("/", methods=["GET"])
def home():
    return "Booking bot is running!"

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
