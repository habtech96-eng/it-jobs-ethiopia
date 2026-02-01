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

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
API_ID = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION")
# FIREBASE_URL መጨረሻው .json መሆኑን እርግጠኛ ሁን
FIREBASE_URL = os.getenv("FIREBASE_URL")
if FIREBASE_URL and not FIREBASE_URL.endswith(".json"):
    FIREBASE_URL += ".json"

IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data", "graphic", "programmer"]
EXCLUDE_WORDS = ["login", "register", "apply", "details", "contact", "join our channel"]
SOURCES = ["https://hahujobs.net/jobs", "https://www.ethiojobs.net", "https://www.elelanajobs.com", "https://www.ezega.com/Jobs/JobVacancies"]

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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    for url in SOURCES:
        try:
            driver.get(url)
            await asyncio.sleep(7) # time.sleep ፋንታ asyncio.sleep መጠቀም ለ async ይመረጣል
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

async def run_telegram_scraper():
    if not STRING_SESSION:
        print("⚠️ Telegram Session የለም፣ ዝለል...")
        return
    print("🚀 Telegram Scraper ተጀመረ...")
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.start()
    
    # እዚህ ጋር ለሙከራ ያህል ለ 1 ደቂቃ ብቻ እንዲቆይ ማድረግ ትችላለህ (GitHub Actions እንዲያበቃ)
    # ወይም በቋሚነት እንዲሰራ ካልፈለግክ ይህን ክፍል መቀየር ይቻላል
    print("📡 አዳዲስ መልእክቶችን በማዳመጥ ላይ...")
    # ማስታወሻ፡ GitHub Actions ላይ በቋሚነት (Listening) እንዲቆይ ማድረግ ሰዓት ይበላል።
    # ስለዚህ ለጊዜው Web Scraper-ን ብቻ ማስኬድ ይሻላል።
    
    await client.disconnect()

async def main():
    # መጀመሪያ Web scraper-ን ጨርስ
    await run_web_scraper()
    # ከዚያ Telegram scraper-ን (አስፈላጊ ከሆነ)
    # await run_telegram_scraper()

if __name__ == "__main__":
    asyncio.run(main())
