# orders.py
import telebot
from telebot.handler_backends import State, StatesGroup
import database
import keyboards
from config import ADMIN_IDS

class CustomerOrderStates(StatesGroup):
    waiting_for_phone = State()     # የስም ደረጃ ተቀንሷል
    waiting_for_location = State()

def register_order_handlers(bot):

    # 🛍️ ደንበኛው "አሁኑኑ እዘዝ" ሲል
    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
    def start_order_flow(call):
        chat_id = call.message.chat.id
        product_id = call.data.replace("buy_", "")
        
        bot.answer_callback_query(call.id)
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            bot.send_message(chat_id, "⚠️ ይቅርታ፣ ይህ ምርት በአሁን ሰዓት አልተገኘም።")
            return
            
        bot.set_state(chat_id, CustomerOrderStates.waiting_for_phone)
        with bot.retrieve_data(chat_id) as data:
            data['product_name'] = product['name']
            # 👤 አውቶማቲክ፦ የስም ስህተትን ለመቀነስ የቴሌግራም ስሙን እዚሁ እንይዛለን
            data['customer_name'] = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
            
        # 📱 አውቶማቲክ የኪቦርድ በተኑን እንልካለን
        bot.send_message(
            chat_id, 
            "📱 ትዕዛዝዎን ለመመዝገብ ከታች ያለውን **'ስልኬን በራስ-ሰር ላክ'** የሚለውን በተን ይጫኑ፦", 
            reply_markup=keyboards.get_phone_keyboard(),
            parse_mode="Markdown"
        )

    # 1️⃣ የስልክ ቁጥር መቀበያ (ከተጫነው በተን ላይ በራስ-ሰር ይነበባል)
    @bot.message_handler(state=CustomerOrderStates.waiting_for_phone, content_types=['contact', 'text'])
    def process_customer_phone(message):
        chat_id = message.chat.id
        
        # ተጠቃሚው በተኑን ተጭኖ ከላከ በ contact ውስጥ ይመጣል (በጣም አስተማማኝ)
        if message.contact is not None:
            phone = message.contact.phone_number
        else:
            # በእጁ ከጻፈም እንዳይበላሽ
            phone = message.text.strip()
            
        with bot.retrieve_data(chat_id) as data:
            data['phone'] = phone
            
        bot.send_message(
            chat_id, 
            "📍 እቃው የሚረከቡበትን አድራሻ ይምረጡ ወይም ይጻፉ፦", 
            reply_markup=keyboards.get_location_keyboard()
        )
        bot.set_state(chat_id, CustomerOrderStates.waiting_for_location)

    # 2️⃣ የአድራሻ መቀበያ እና ማጠቃለያ
    @bot.message_handler(state=CustomerOrderStates.waiting_for_location)
    def process_customer_location(message):
        chat_id = message.chat.id
        location = message.text.strip()
        
        with bot.retrieve_data(chat_id) as data:
            product_name = data['product_name']
            customer_name = data['customer_name']
            phone = data['phone']
            
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (user_name, chat_id, product_name, phone) VALUES (?, ?, ?, ?)",
                (customer_name, chat_id, product_name, phone)
            )
            conn.commit()
            order_id = cursor.lastrowid
            conn.close()
            
        bot.delete_state(chat_id)
        
        success_msg = f"🎉 **ትዕዛዝዎ በተሳካ ሁኔታ ተመዝግቧል!**\n\n🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n👟 **የመረጡት ምርት፦** {product_name}\n👤 **የአስረካቢ ስም፦** {customer_name} (Auto)\n📞 **ስልክ፦** {phone} (Auto)\n📍 **ቦታ፦** {location}\n\n⏳ አድሚኑ ትዕዛዝዎን አይቶ በቅርቡ ያነጋግርዎታል። እናመሰግናለን!"
        bot.send_message(chat_id, success_msg, parse_mode="Markdown", reply_markup=keyboards.get_main_menu())
        
        admin_alert = f"⚠️ **አዲስ ትዕዛዝ ገብቷል!**\n\n🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n👤 **ደንበኛ፦** {customer_name}\n👟 **ምርት፦** {product_name}\n📞 **ስልክ:** {phone}"
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, admin_alert, parse_mode="Markdown")
            except Exception as e:
                print(f"Admin Notify Error: {e}")