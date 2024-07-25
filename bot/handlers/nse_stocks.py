import asyncio
import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger
import requests


STOCK_DETAILS_URL = 'https://www.nseindia.com/api/quote-equity?symbol={symbol}'
AUTOCOMPLETE_URL = 'https://www.nseindia.com/api/search/autocomplete?q={query}'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}


def fetch_stock_details(symbol: str) -> dict:
    """
    Fetch stock details for a given symbol from NSE India.

    Args:
        symbol (str): The stock symbol to fetch details for.

    Returns:
        dict: The stock details.
    """
    url = STOCK_DETAILS_URL.format(symbol=symbol)
    logger.info(f"Fetching stock details for symbol: {symbol}")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        stock_details = response.json()
        logger.debug(f"Stock details fetched: {stock_details}")
        return stock_details
    except requests.RequestException as e:
        logger.error(f"Error fetching stock details: {e}")
        return {}


async def remember_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) != 2:
        await update.message.reply_text("Usage: /remember_stock <STOCK_SYMBOL>")
        return

    stock_symbol = text[1].upper()
    stock_details = await asyncio.to_thread(fetch_stock_details, stock_symbol)

    if not stock_details:
        await update.message.reply_text(f"Could not fetch details for stock symbol: {stock_symbol}")
        return

    stock_name = stock_details['info']['companyName']
    stock_price = stock_details['priceInfo']['lastPrice']

    async with aiosqlite.connect('stocks.db') as db:
        async with db.execute('''
            SELECT 1 FROM user_stocks WHERE user_id=? AND stock_symbol=?
        ''', (user_id, stock_symbol)) as cursor:
            existing_stock = await cursor.fetchone()

        if existing_stock:
            await update.message.reply_text(f"You already have the stock {stock_name} ({stock_symbol}) remembered.")
            return

        await db.execute('''
            INSERT INTO user_stocks (user_id, stock_symbol, stock_name, stock_price) VALUES (?, ?, ?, ?)
        ''', (user_id, stock_symbol, stock_name, stock_price))
        await db.commit()

    await update.message.reply_text(f"Stock {stock_name} ({stock_symbol}) at price {stock_price} remembered for you and added to the global list.")


async def fetch_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    async with aiosqlite.connect('stocks.db') as db:
        async with db.execute('''
            SELECT stock_symbol, stock_name, stock_price FROM user_stocks WHERE user_id=?
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await update.message.reply_text("You have no remembered stocks.")
        return

    message = "Your remembered stocks:\n"
    for row in rows:
        message += f"{row[1]} ({row[0]}): {row[2]}\n"

    await update.message.reply_text(message)
