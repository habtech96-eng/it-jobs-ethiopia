import os
import re
import time
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION (Secrets) ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID") # የአንተ ቻናል ID
FIREBASE_URL = os.getenv("FIREBASE_URL")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION")

# IT Keywords
IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data", "graphic", "programmer"]
EXCLUDE_WORDS = ["login", "register", "apply", "details", "contact", "join our channel"]

# --- 1. WEB SCRAPER SECTION ---
SOURCES = [
    "https://hahujobs.net/jobs", "https://www.ethiojobs.net", 
    "https://www.elelanajobs.com", "https://www.ezega.com/Jobs/JobVacancies"
]

def is_already_sent(title):
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                if data[key].get('title').strip().lower() == title.strip().lower(): return True
    except: pass
    return False

def save_to_firebase(title):
    try: requests.post(FIREBASE_URL, json={"title": title, "time": time.ctime()})
    except: pass

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

async def run_web_scraper():
    print("🚀 Web Scraper ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    for url in SOURCES:
        try:
            driver.get(url)
            time.sleep(7)
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                if len(title) > 10:
                    title_low = title.lower()
                    if any(word in title_low for word in IT_KEYWORDS) and not any(w in title_low for w in EXCLUDE_WORDS):
                        if not is_already_sent(title) and href:
                            source_name = url.split('/')[2].replace('www.', '')
                            msg = f"<b>💻 አዲስ የ IT ስራ (ከድረ-ገጽ)</b>\n\n💼 <b>ስራ፡</b> {title}\n🌐 <b>ምንጭ፡</b> {source_name}\n\n🔗 <a href='{href}'>ዝርዝሩን እዚህ ይመልከቱ</a>"
                            send_to_telegram(msg)
                            save_to_firebase(title)
        except Exception as e: print(f"❌ ስህተት በ {url}: {e}")
    driver.quit()

# --- 2. TELEGRAM SCRAPER SECTION ---
TARGET_CHANNELS = ['effoyjobs', 'elelanajobs', 'freelance_ethio', 'hahujobs', 'ethiojobsofficial']

def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    return text.strip()

async def run_telegram_scraper():
    print("🚀 Telegram Scraper ተጀመረ...")
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.start()
    
    @client.on(events.NewMessage(chats=TARGET_CHANNELS))
    async def handler(event):
        msg_text = event.message.message
        if msg_text and any(word.lower() in msg_text.lower() for word in IT_KEYWORDS):
            if not is_already_sent(msg_text[:50]): # የመጀመሪያ 50 ፊደላት ለFirebase
                cleaned = clean_text(msg_text)
                final_msg = f"<b>💻 አዲስ የ IT ስራ (ከቴሌግራም)</b>\n\n{cleaned}"
                send_to_telegram(final_msg)
                save_to_firebase(msg_text[:50])
    
    await client.run_until_disconnected()

# --- MAIN RUNNER ---
if __name__ == "__main__":
    # Web scraperን አንዴ ያካሂዳል
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_web_scraper())
    # Telegram scraperን በቋሚነት ያስነሳል
    loop.run_until_complete(run_telegram_scraper())
