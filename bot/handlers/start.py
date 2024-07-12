from telegram import Update
from telegram.ext import ContextTypes


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = f"Hi {update.effective_user.first_name}, \n I am Krill, your stock adviser."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
    )
