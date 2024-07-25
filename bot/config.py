from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")


def setup_database():
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_stocks (
            user_id INTEGER,
            stock_symbol TEXT,
            stock_name TEXT,
            stock_price REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS global_stocks (
            stock_symbol TEXT,
            stock_name TEXT,
            stock_price REAL
        )
    ''')
    conn.commit()
    conn.close()


setup_database()
