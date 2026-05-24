# database.py
import sqlite3
import subprocess
import os

DB_NAME = "shoe_store.db"

# 🔄 ዳታቤዙ ሲቀየር በራስ-ሰር ወደ GitHub የመግፊያ ፈንክሽን
def backup_to_github():
    try:
        # Render ላይ የGit መለያህን ለጊዜው ማስተዋወቅ (ስህተት እንዳይፈጥር)
        subprocess.run(["git", "config", "user.name", "Render Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@render.com"], check=True)
        
        # ፋይሉን Add, Commit እና Push ማድረግ
        subprocess.run(["git", "add", DB_NAME], check=True)
        # [skip ci] የሚለው ጥቅስ Render ያለምክንያት ደጋግሞ አፕዴት እንዳያደርግ ይከለክላል
        subprocess.run(["git", "commit", "-m", "🔄 Auto-backup database [skip ci]"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ ዳታቤዙ በተሳካ ሁኔታ ወደ GitHub ተገፍቷል!")
    except Exception as e:
        print(f"⚠️ ወደ GitHub መግፋት አልተሳካም (ምናልባት አዲስ ዳታ ስለሌለ ይሆናል)፦ {e}")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. የምርቶች ሰንጠረዥ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price TEXT NOT NULL,
            size TEXT NOT NULL,
            photo TEXT, 
            stock TEXT DEFAULT '10'
        )
    """)
    
    # 2. የትዕዛዞች ሰንጠረዥ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            chat_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT DEFAULT '⏱️ ይጠበቃል'
        )
    """)
    
    conn.commit()
    conn.close()

# ➕ አዲስ ምርት ሲጨመር
def add_product(name, category, price, size, photo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, size, photo) VALUES (?, ?, ?, ?, ?)",
        (name, category, price, size, photo_id)
    )
    conn.commit()
    conn.close()
    backup_to_github() # 👈 ወደ ጂትሀብ ይላክ

# 🛍️ አዲስ ትዕዛዝ (Order) ሲጨመር (ይህንን ፈንክሽን በሌላ ፋይል የምትጠቀመው ከሆነ እዚያ ላይ backup_to_github() ጨምርበት)
def add_order(user_name, chat_id, product_name, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (user_name, chat_id, product_name, phone) VALUES (?, ?, ?, ?)",
        (user_name, chat_id, product_name, phone)
    )
    conn.commit()
    conn.close()
    backup_to_github() # 👈 ወደ ጂትሀብ ይላክ

def get_products_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_orders(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]