from telegram import Update
from telegram.ext import ContextTypes
import logging


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # NOT USED YET: SETUP GROUP PRIVACY IN BOT FATHER TO ENABLE THIS FEATURE
    chat_id = update.effective_chat.id
    message = update.message.text
    logging.info(f"Message received in chat {chat_id}: {message}")

    # Respond to the message
    await context.bot.send_message(chat_id=chat_id, text=f"You said: {message}")
