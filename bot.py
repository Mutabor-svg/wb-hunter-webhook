import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
app = Flask(__name__)
watched_items = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Бот работает через webhook.")

def add(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not context.args or not context.args[0].isdigit():
        update.message.reply_text("Укажи ID товара. Пример: /add 12345678")
        return
    product_id = int(context.args[0])
    watched_items.setdefault(chat_id, set()).add(product_id)
    update.message.reply_text(f"Товар {product_id} добавлен.")

def list_items(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    items = watched_items.get(chat_id, [])
    if not items:
        update.message.reply_text("Ты ничего не отслеживаешь.")
    else:
        msg = "📦 Твои товары:\n" + "\n".join(f"- {i}" for i in items)
        update.message.reply_text(msg)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

logging.basicConfig(level=logging.INFO)
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("add", add))
dispatcher.add_handler(CommandHandler("list", list_items))

@app.before_first_request
def setup():
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    print(f"Webhook установлен: {WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))