import asyncio
import aiohttp
import aiosqlite
from bot.config import ALPHA_VANTAGE_API_KEY
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger


async def extract_inr_currency(json_data):
    logger.debug("Extracting INR currency from JSON data.")
    for match in json_data.get("bestMatches", []):
        if match.get("8. currency") == "INR":
            logger.debug(f"INR currency found: {match}")
            return match
    logger.debug("INR currency not found.")
    return None


async def extract_inr_symbol(json_data):
    logger.debug("Extracting INR symbol from JSON data.")
    match = await extract_inr_currency(json_data)
    if match:
        symbol = match.get("1. symbol")
        logger.debug(f"INR symbol extracted: {symbol}")
        return symbol
    logger.debug("No INR symbol found.")
    return None


async def fetch_stock_symbol(keyword):
    logger.info(f"Fetching stock symbol for keyword: {keyword}")
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={ALPHA_VANTAGE_API_KEY}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            print(f"\x1b[32;41m{data}\x1b[0m")
    symbol = await extract_inr_symbol(data)
    if symbol:
        logger.info(f"Stock symbol fetched: {symbol}")
    else:
        logger.warning(f"No stock symbol found for keyword: {keyword}")
    return symbol


async def main():
    symbol = await fetch_stock_symbol('rvnl')
    print(symbol)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())


async def get_stock_details(stock_symbol):
    logger.info(f"Getting stock details for symbol: {stock_symbol}")
    symbol_find = await fetch_stock_symbol(stock_symbol)
    if not symbol_find:
        logger.warning(f"No symbol found for stock: {stock_symbol}")
        return None

    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol_find}&apikey={ALPHA_VANTAGE_API_KEY}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    if 'Global Quote' in data:
        quote = data['Global Quote']
        stock_name = stock_symbol  # Alpha Vantage does not provide stock name directly
        stock_price = float(quote['05. price'])
        logger.info(
            f"Stock details fetched: {stock_symbol}, {stock_name}, {stock_price}")
        return stock_symbol, stock_name, stock_price
    else:
        logger.warning(
            f"Could not fetch details for stock symbol: {stock_symbol}")
        return None


async def remember_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    stock_symbol = ' '.join(context.args).upper()
    logger.info(f"Remembering stock for user {user_id}: {stock_symbol}")

    if not stock_symbol:
        logger.warning("No stock symbol provided.")
        await update.message.reply_text("Please provide a stock symbol.")
        return

    stock_details = await get_stock_details(stock_symbol)
    if not stock_details:
        logger.warning(
            f"Could not fetch details for stock symbol {stock_symbol}.")
        await update.message.reply_text(f"Could not fetch details for stock symbol {stock_symbol}.")
        return

    stock_symbol, stock_name, stock_price = stock_details

    async with aiosqlite.connect('stocks.db') as conn:
        async with conn.cursor() as c:
            await c.execute('INSERT INTO user_stocks (user_id, stock_symbol, stock_name, stock_price) VALUES (?, ?, ?, ?)',
                            (user_id, stock_symbol, stock_name, stock_price))
            await c.execute('INSERT INTO global_stocks (stock_symbol, stock_name, stock_price) VALUES (?, ?, ?)',
                            (stock_symbol, stock_name, stock_price))
            await conn.commit()

    logger.info(
        f"Stock {stock_name} ({stock_symbol}) remembered for user {user_id}.")
    await update.message.reply_text(f"Stock {stock_name} ({stock_symbol}) at price {stock_price} remembered for you and added to the global list.")


async def fetch_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args
    fetch_all = len(args) > 0 and args[0].lower() == 'all'

    logger.info(f"Fetching stocks for user {user_id}, fetch all: {fetch_all}")

    async with aiosqlite.connect('stocks.db') as conn:
        async with conn.cursor() as c:
            if fetch_all:
                await c.execute('SELECT stock_symbol, stock_name, stock_price FROM global_stocks')
                stocks = await c.fetchall()
                message = "Global stock list:\n"
            else:
                await c.execute('SELECT stock_symbol, stock_name, stock_price FROM user_stocks WHERE user_id = ?', (user_id,))
                stocks = await c.fetchall()
                message = "Your remembered stocks:\n"

    stock_list = [f"{stock[1]} ({stock[0]}): {stock[2]}" for stock in stocks]
    message += "\n".join(stock_list) if stock_list else "No stocks found."

    logger.info(f"Stocks fetched for user {user_id}.")
    await update.message.reply_text(message)
