# orders.py
import telebot
from telebot.handler_backends import State, StatesGroup
import database
import keyboards
from config import ADMIN_IDS
from receipt import generate_receipt_image
import os

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
        # 💡 ለደረሰኙ እንዲጠቅመን ዋጋ (price) እና ሳይዝ (size) አብረን እንወስዳለን
        cursor.execute("SELECT name, price, size FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            bot.send_message(chat_id, "⚠️ ይቅርታ፣ ይህ ምርት በአሁን ሰዓት አልተገኘም።")
            return
            
        bot.set_state(chat_id, CustomerOrderStates.waiting_for_phone)
        with bot.retrieve_data(chat_id) as data:
            data['product_name'] = product['name']
            data['price'] = product['price']
            data['size'] = product['size']
            # 👤 አውቶማቲክ፦ የስም ስህተትን ለመቀነስ የቴሌግራም ስሙን እዚሁ እንይዛለን
            data['customer_name'] = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
            
        # 📱 አውቶማቲክ የኪቦርድ በተኑን እንልካለን
        bot.send_message(
            chat_id, 
            "📱 ትዕዛዝዎን ለመመዝገብ ከታች ያለውን **'ስልኬን በራስ-ሰር ላክ'** የሚለውን በተን ይጫኑ፦", 
            reply_markup=keyboards.get_phone_keyboard(),
            parse_mode="Markdown"
        )

    # 1️⃣ የስልክ ቁጥር መቀበያ
    @bot.message_handler(state=CustomerOrderStates.waiting_for_phone, content_types=['contact', 'text'])
    def process_customer_phone(message):
        chat_id = message.chat.id
        
        if message.contact is not None:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()
            
        with bot.retrieve_data(chat_id) as data:
            data['phone'] = phone
            
        bot.send_message(
            chat_id, 
            "📍 እቃው የሚረከቡበትን አድራሻ ይምረጡ ወይም ይጻፉ፦", 
            reply_markup=keyboards.get_location_keyboard()
        )
        bot.set_state(chat_id, CustomerOrderStates.waiting_for_location)

    # 2️⃣ የአድራሻ መቀበያ፣ ማጠቃለያ እና የደረሰኝ መላኪያ
    @bot.message_handler(state=CustomerOrderStates.waiting_for_location)
    def process_customer_location(message):
        chat_id = message.chat.id
        location = message.text.strip()
        
        with bot.retrieve_data(chat_id) as data:
            product_name = data['product_name']
            customer_name = data['customer_name']
            phone = data['phone']
            price = data['price']
            size = data['size']
            
            # 1. ኦርደሩን በዳታቤዝ ውስጥ መመዝገብ
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (user_name, chat_id, product_name, phone) VALUES (?, ?, ?, ?)",
                (customer_name, chat_id, product_name, phone)
            )
            conn.commit()
            order_id = cursor.lastrowid
            conn.close()
            
        # ስቴቱን ማጽዳት
        bot.delete_state(chat_id)
        
        # 2. ለደንበኛው የጽሑፍ ማረጋገጫ መላክ
        success_msg = f"🎉 **ትዕዛዝዎ በተሳካ ሁኔታ ተመዝግቧል!**\n\n🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n👟 **የመረጡት ምርት፦** {product_name}\n👤 **የደንበኛ ስም፦** {customer_name} (Auto)\n📞 **ስልክ፦** {phone} (Auto)\n📍 **ቦታ፦** {location}\n\n⏳ አድሚኑ ትዕዛዝዎን አይቶ በቅርቡ ያነጋግርዎታል። እናመሰግናለን!"
        bot.send_message(chat_id, success_msg, parse_mode="Markdown", reply_markup=keyboards.get_main_menu())
        
        # 🧾 3. እውነተኛ የፎቶ ደረሰኝ በኮድ ማመንጨት (አዲስ የተጨመረ)
        try:
            receipt_file = generate_receipt_image(
                order_id=order_id, 
                user_name=customer_name, 
                product_name=product_name, 
                price=price, 
                size=size, 
                phone=phone
            )
            
            # ፎቶውን ለደንበኛው መላክ
            with open(receipt_file, 'rb') as photo:
                bot.send_photo(
                    chat_id=chat_id, 
                    photo=photo, 
                    caption=f"🧾 የእርስዎ እውነተኛ ዲጂታል ደረሰኝ ተዘጋጅቷል!\nእባክዎ ይህንን ለባለቤቱ አስተላልፈው ክፍያ ይፈጽሙ።"
                )
            
            # ፋይሉን ከሰርቨር ላይ ማጽዳት
            if os.path.exists(receipt_file):
                os.remove(receipt_file)
        except Exception as receipt_error:
            print(f"⚠️ Receipt Generation Error: {receipt_error}")

        # 4. ለአድሚን መረጃ መላክ
        admin_alert = f"⚠️ **አዲስ ትዕዛዝ ገብቷል!**\n\n🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n👤 **ደንበኛ፦** {customer_name}\n👟 **ምርት፦** {product_name}\n📞 **ስልክ፦** {phone}\n📍 **አድራሻ፦** {location}"
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, admin_alert, parse_mode="Markdown")
            except Exception as e:
                print(f"Admin Notify Error: {e}")