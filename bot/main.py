import logging

from telegram.ext import ApplicationBuilder, \
    CommandHandler, MessageHandler, filters

from bot.handlers import handle_message, command_start, \
    command_resp
from bot.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', command_start))
    application.add_handler(CommandHandler('resp', command_resp))
    application.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()
