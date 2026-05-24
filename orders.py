# orders.py
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import database
import keyboards
from config import ADMIN_IDS
from receipt import generate_receipt_image
import os

class CustomerOrderStates(StatesGroup):
    waiting_for_phone = State()
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
            data['customer_name'] = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
            
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
        phone = message.contact.phone_number if message.contact is not None else message.text.strip()
            
        with bot.retrieve_data(chat_id) as data:
            data['phone'] = phone
            
        bot.send_message(
            chat_id, 
            "📍 እቃው የሚረከቡበትን አድራሻ ይምረጡ ወይም ይጻፉ፦", 
            reply_markup=keyboards.get_location_keyboard()
        )
        bot.set_state(chat_id, CustomerOrderStates.waiting_for_location)

    # 2️⃣ የአድራሻ መቀበያ፣ ማጠቃለያ እና ትዕዛዝ ለባለቤቱ መላኪያ
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
            
            # 💡 ለውጥ፦ ፕራይስ እና ሳይዝን በዳታቤዝ ውስጥ አብረን እናስቀምጣለን (ካልተፈጠሩ ALTER TABLE አድርጋቸው)
            conn = database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO orders (user_name, chat_id, product_name, phone, price, size) VALUES (?, ?, ?, ?, ?, ?)",
                    (customer_name, chat_id, product_name, phone, price, size)
                )
            except Exception:
                # የድሮ ሰንጠረዥ ከሆነ ያለ ፕራይስ እና ሳይዝ ይሞክራል
                cursor.execute(
                    "INSERT INTO orders (user_name, chat_id, product_name, phone) VALUES (?, ?, ?, ?)",
                    (customer_name, chat_id, product_name, phone)
                )
            conn.commit()
            order_id = cursor.lastrowid
            conn.close()
            
        bot.delete_state(chat_id)
        
        success_msg = (
            f"🎉 **ትዕዛዝዎ በተሳካ ሁኔታ ተመዝግቧል!**\n\n"
            f"🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n"
            f"👟 **ምርት፦** {product_name} (Size: {size})\n"
            f"💰 **ዋጋ፦** {price} ETB\n"
            f"📍 **አድራሻ፦** {location}\n\n"
            f"⏳ **ቀጣይ ደረጃ፦** አድሚኑ ትዕዛዝዎን አይቶ የክፍያ መረጃ ይልክልዎታል። እባክዎ በትዕግስት ይጠብቁ!"
        )
        bot.send_message(chat_id, success_msg, parse_mode="Markdown", reply_markup=keyboards.get_main_menu())
        
        # 💡 የቴሌግራም 64-byte ሊሚትን ላለመጨረስ Callback Dataዎቹን እጅግ አሳጥረናቸዋል!
        admin_markup = InlineKeyboardMarkup()
        admin_markup.row(
            InlineKeyboardButton("💳 Send Payment Info", callback_data=f"sendpay_{order_id}"),
            InlineKeyboardButton("❌ Reject Order", callback_data=f"rj_{order_id}")
        )
        
        admin_alert = (
            f"⚠️ **አዲስ ትዕዛዝ ገብቷል!**\n\n"
            f"🆔 **የትዕዛዝ ቁጥር፦** #{order_id}\n"
            f"👤 **ደንበኛ፦** {customer_name}\n"
            f"👟 **ምርት፦** {product_name} (Size: {size})\n"
            f"📞 **ስልክ፦** {phone}\n"
            f"📍 **አድራሻ፦** {location}\n"
            f"💵 **ክፍያ፦** {price} ETB\n\n"
            f"👉 ትዕዛዙን ተቀብለው ለደንበኛው የባንክ አካውንት ለመላክ **Send Payment Info** የሚለውን ይጫኑ።"
        )
        
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, admin_alert, parse_mode="Markdown", reply_markup=admin_markup)
            except Exception as e:
                print(f"Admin Notify Error: {e}")

    # 3️⃣ 🎯 የደረጃ በደረጃ በይነገጽ (Interaction Logic)
    @bot.callback_query_handler(func=lambda call: any(call.data.startswith(prefix) for prefix in ["sendpay_", "paid_", "finalapp_", "rj_"]))
    def handle_interactive_workflow(call):
        bot.answer_callback_query(call.id)
        action_data = call.data.split("_")
        action = action_data[0]
        order_id = action_data[1]
        
        # ሁሉንም መረጃ ሁልጊዜ ከዳታቤዝ በ Order ID በታማኝነት መውሰድ (ምንም ዳታ አይጠፋም)
        conn = database.get_connection()
        conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            bot.send_message(call.message.chat.id, "⚠️ ስህተት፦ ይህ ትዕዛዝ በዳታቤዝ ውስጥ አልተገኘም።")
            return
            
        user_chat_id = order['chat_id']
        # ዋጋ እና ሳይዝ ከ orders ቴብል ከሌሉ ከምርቱ ፈልጎ እንዲያወጣ መከላከያ (Fallback)
        price = order.get('price') or "0"
        size = order.get('size') or "N/A"

        # -------------------------------------------------------------
        # STEP A: አድሚኑ "Send Payment Info" ሲጫን
        # -------------------------------------------------------------
        if action == "sendpay":
            bot.edit_message_text(f"⏳ ለትዕዛዝ #{order_id} የክፍያ መረጃ ለደንበኛው ተልኳል። ደንበኛው ክፍያ እስኪፈጽም ይጠበቃል።", call.message.chat.id, call.message.message_id)
            
            pay_markup = InlineKeyboardMarkup()
            pay_markup.add(InlineKeyboardButton("✅ ክፍያ ፈጽሜያለሁ / I have Paid", callback_data=f"paid_{order_id}"))
            
            payment_details = (
                f"💳 **የትዕዛዝ ቁጥር #{order_id} የክፍያ መረጃ**\n\n"
                f"💵 **ጠቅላላ የሚከፈል፦** {price} ETB\n\n"
                f"📌 **የባንክ አካውንቶች፦**\n"
                f"• ንግድ ባንክ (CBE)፦ `1000274286637`\n"
                f"• አቢሲኒያ ባንክ፦ `150662915`\n"
                f"• Telebirr፦ `0938649925`\n\n"
                f"👉 ክፍያውን እንደፈጸሙ የከፈሉበትን ደረሰኝ (Screenshot) ለባለቤቱ [@hab7tech] ይላኩ። "
                f"ከዚያም ከታች ያለውን **'ክፍያ ፈጽሜያለሁ'** የሚለውን በተን መጫን እንዳይረሱ! 👇"
            )
            bot.send_message(user_chat_id, payment_details, parse_mode="Markdown", reply_markup=pay_markup)

        # -------------------------------------------------------------
        # STEP B: ደንበኛው "ክፍያ ፈጽሜያለሁ" ሲል
        # -------------------------------------------------------------
        elif action == "paid":
            bot.edit_message_text(f"⏳ ማሳወቂያዎ ለአድሚን ደርሷል። ክፍያዎ ተረጋግጦ የመጨረሻው ዲጂታል ደረሰኝ በቅርቡ ይላክለታል።", call.message.chat.id, call.message.message_id)
            
            confirm_markup = InlineKeyboardMarkup()
            confirm_markup.row(
                InlineKeyboardButton("✅ Approve Payment & Send Receipt", callback_data=f"finalapp_{order_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rj_{order_id}")
            )
            
            # ማሳወቂያውን ለሁሉም አድሚኖች መላክ
            for admin_id in ADMIN_IDS:
                try:
                    bot.send_message(
                        admin_id, 
                        f"💰 **የክፍያ ማሳወቂያ (ትዕዛዝ #{order_id})!**\n\nደንበኛው **{order['user_name']}** ክፍያ መፈጸሙን አሳውቋል። እባክዎ ባንክዎን ያረጋግጡና ክፍያው ከገባ **Approve Payment** የሚለውን ይጫኑ።",
                        reply_markup=confirm_markup
                    )
                except Exception as e:
                    print(f"Admin Notify Paid Error: {e}")

        # -------------------------------------------------------------
        # STEP C: አድሚኑ "Approve Payment" ሲል (የመጨረሻው ደረጃ)
        # -------------------------------------------------------------
        elif action == "finalapp":
            bot.edit_message_text(f"✅ ለትዕዛዝ #{order_id} ክፍያው ጽድቋል! ኦፊሴላዊ የሽያጭ ማረጋገጫ ደረሰኝ ለደንበኛው ተልኳል።", call.message.chat.id, call.message.message_id)
            bot.send_message(user_chat_id, f"🎉 **ክፍያዎ ተረጋግጧል!**\nየትዕዛዝ ቁጥር #{order_id} ሙሉ በሙሉ ተጠናቋል።")
            
            try:
                receipt_file = generate_receipt_image(order_id, order['user_name'], order['product_name'], price, size, order['phone'])
                with open(receipt_file, 'rb') as photo:
                    bot.send_photo(
                        chat_id=user_chat_id, 
                        photo=photo, 
                        caption=f"🧾 **ኦፊሴላዊ የክፍያ ማረጋገጫ ደረሰኝ (Official Payment Receipt)**\n\nስለ ክፍያዎ እና ስለ እምነትዎ እጅግ እናመሰግናለን! ምርትዎ በቅርቡ አድራሻዎ ላይ ይደርሳል።"
                    )
                if os.path.exists(receipt_file):
                    os.remove(receipt_file)
            except Exception as e:
                print(f"Receipt Generation/Sending Error: {e}")
                bot.send_message(user_chat_id, "⚠️ ደረሰኝ ማመንጨት ላይ ስህተት አጋጥሟል፣ ነገር ግን ክፍያዎ ተረጋግጧል።")

        # -------------------------------------------------------------
        # STEP D: አድሚኑ ውድቅ (Reject) ሲያደርግ
        # -------------------------------------------------------------
        elif action == "rj":
            bot.edit_message_text(f"❌ ትዕዛዝ #{order_id} ውድቅ ተደርጓል።", call.message.chat.id, call.message.message_id)
            bot.send_message(user_chat_id, f"❌ **ይቅርታ፦** የትዕዛዝ ቁጥር #{order_id} በአድሚኑ ውድቅ ተደርጓል (ተሰርዟል)።")