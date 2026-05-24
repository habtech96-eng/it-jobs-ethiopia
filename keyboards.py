from telebot import types

# ⌨️ የዋና ማውጫ በተኖች (Main Menu)
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👟 ምርቶችን እይ")
    btn2 = types.KeyboardButton("📞 እኛን ለማግኘት")
    btn3 = types.KeyboardButton("🛍️ የእኔ ትዕዛዞች")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup

# 🗂️ የምድብ ማውጫ በተኖች (Category Menu)
def get_category_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👞 የወንዶች ጫማዎች")
    btn2 = types.KeyboardButton("👠 የሴቶች ጫማዎች")
    btn3 = types.KeyboardButton("🔄 ወደ ዋና ማውጫ")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

# 🛍️ የእያንዳንዱ ምርት መግዣ በተን (Inline Button)
def get_buy_inline_keyboard(product_id):
    inline_markup = types.InlineKeyboardMarkup()
    buy_btn = types.InlineKeyboardButton("🛍️ አሁኑኑ እዘዝ", callback_data=f"buy_{product_id}")
    inline_markup.add(buy_btn)
    return inline_markup

    # keyboards.py (ከቀድሞው ኮድ በታች የሚቀጥል)

# 👨‍💼 የአድሚን ዋና ማውጫ (የተራ ደንበኛ ማውጫ + የአድሚን በተን)
def get_admin_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👟 ምርቶችን እይ")
    btn2 = types.KeyboardButton("📞 እኛን ለማግኘት")
    btn3 = types.KeyboardButton("🛍️ የእኔ ትዕዛዞች")
    btn_admin = types.KeyboardButton("🔐 Admin Panel") # 👈 ለአድሚን ብቻ የሚታይ
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn_admin)
    return markup

# 🛠️ የአድሚን መቆጣጠሪያ ሰሌዳ (Inline Buttons)
def get_admin_panel_keyboard():
    inline_markup = types.InlineKeyboardMarkup(row_width=1)
    btn_view_orders = types.InlineKeyboardButton("📋 ሁሉንም ትዕዛዞች እይ", callback_data="admin_view_orders")
    btn_add_product = types.InlineKeyboardButton("➕ አዲስ ምርት ጨምር", callback_data="admin_add_product")
    inline_markup.add(btn_view_orders, btn_add_product)
    return inline_markup 

# keyboards.py (ከፋይሉ መጨረሻ ላይ ቀጥሎ የሚጻፍ)

# 📞 የቴሌግራም ስልክ ቁጥርን በራሱ አውቶማቲክ የሚያመጣ በተን
def get_phone_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # request_contact=True ሲሆን ስልኩን በራሱ ይልካል
    btn_phone = types.KeyboardButton("📱 ስልኬን በራስ-ሰር ላክ (Share Contact)", request_contact=True)
    markup.add(btn_phone)
    return markup

# 📍 ለአድራሻ የሚሆኑ ቀላሉ አማራጮች በተን
def get_location_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("📍 አዲስ አበባ (ከተማ ውስጥ)")
    btn2 = types.KeyboardButton("🚚 በፖስታ/በመኪና (ከአዲስ አበባ ውጭ)")
    markup.add(btn1, btn2)
    return markup