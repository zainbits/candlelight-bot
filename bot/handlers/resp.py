from telegram import Update
from telegram.ext import ContextTypes


async def command_resp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the text following the command
    print(f"\x1b[32;41mcontext args are => {context.args}\x1b[0m")
    user_text = ' '.join(context.args)

    if user_text:
        response_text = f"You said: {user_text}"
    else:
        response_text = "You didn't provide any text."

    await update.message.reply_text(text=response_text)
