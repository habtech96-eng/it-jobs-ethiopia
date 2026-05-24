# bot.py
import telebot
from telebot.storage import StateMemoryStorage
from config import BOT_TOKEN
from handlers import register_handlers
from admin import register_admin_handlers
from orders import register_order_handlers # 👈 አዲሱን የትዕዛዝ ፋይል አመጣን
import database

database.init_db()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

# መቆጣጠሪያዎችን መመዝገብ (ቅደም ተከተላቸው እንዳይቀየር)
register_admin_handlers(bot)
register_order_handlers(bot) # 👈 እዚህ ጋ መዘገብነው
register_handlers(bot)

if __name__ == "__main__":
    print("🚀 ቦቱ ከትዕዛዝ መቀበያ እና ከ SQLite ዳታቤዝ ጋር በተሳካ ሁኔታ ተነስቷል...")
    bot.infinity_polling()