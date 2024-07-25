from telegram.ext import ApplicationBuilder, \
    CommandHandler, MessageHandler, filters

from bot.handlers import handle_message, command_start, \
    command_resp
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.nse_stocks import fetch_stocks, remember_stock


if __name__ == '__main__':
    application = ApplicationBuilder().token(
        TELEGRAM_BOT_TOKEN).read_timeout(10).build()

    application.add_handler(CommandHandler('start', command_start))
    application.add_handler(CommandHandler('resp', command_resp))
    application.add_handler(CommandHandler('remember', remember_stock))
    application.add_handler(CommandHandler('stocks', fetch_stocks))
    application.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()
