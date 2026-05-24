# bot.py
import telebot
from telebot.storage import StateMemoryStorage
from config import BOT_TOKEN
from handlers import register_handlers
from admin import register_admin_handlers
from orders import register_order_handlers
import database
import time
import requests
from flask import Flask
from threading import Thread

# 1. ዳታቤዝ ማስጀመር
database.init_db()

# 2. ቦቱን ማዘጋጀት
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

register_admin_handlers(bot)
register_order_handlers(bot)
register_handlers(bot)

# 🌐 3. ለRender መሸወጃ የሚሆን የFlask ዌብ ሰርቨር መፍጠር
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Live!"

def run_flask():
    # Render በዲፎልት 10000 ፖርት ላይ ነው የሚፈልገው
    app.run(host='0.0.0.0', port=10000)

# ቦቱን የማስነሻ ዋና ፈንክሽን
def run_bot():
    print("🚀 ቦቱ መነሳት ጀምሯል...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, Exception) as e:
            print(f"⚠️ የኔትወርክ መቆራረጥ ገጥሟል፣ ከ 5 ሰከንድ በኋላ ይነሳል... [ስህተት፦ {e}]")
            time.sleep(5)
            continue

if __name__ == "__main__":
    # የFlask ዌብ ሰርቨሩን ከበስተጀርባ በThread ማስነሳት
    t = Thread(target=run_flask)
    t.start()
    
    # ቦቱን ማስነሳት
    run_bot()