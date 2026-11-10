import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

def init_db():
    conn = sqlite3.connect("penzugyek.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            type TEXT,
            amount INTEGER,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_transaction(user, t_type, amount, desc):
    conn = sqlite3.connect("penzugyek.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user, type, amount, description) VALUES (?, ?, ?, ?)",
                   (user, t_type, amount, desc))
    conn.commit()
    conn.close()

def get_summary():
    conn = sqlite3.connect("penzugyek.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='bevétel'")
    b = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='kiadás'")
    k = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='várható_bevétel'")
    vb = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='várható_kiadás'")
    vk = cursor.fetchone()[0] or 0
    conn.close()
    return {
        "egyenleg": b - k,
        "osszes_bevétel": b + vb,
        "osszes_kiadás": k + vk,
        "varhato_egyenleg": (b + vb) - (k + vk)
    }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.first_name
    text_lower = text.lower()
    import re
    numbers = re.findall(r'\d+', text.replace(' ', ''))
    if not numbers:
        return
    amount = int(numbers[0])
    if "várható kiadás" in text_lower or "tervezett kiadás" in text_lower:
        save_transaction(user, "várható_
                         
