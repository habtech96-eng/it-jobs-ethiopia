import os
import re
import time
import requests
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
API_ID = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION")
FIREBASE_URL = os.getenv("FIREBASE_URL")

if FIREBASE_URL and not FIREBASE_URL.endswith(".json"):
    FIREBASE_URL += ".json"

IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data", "graphic", "programmer"]
TARGET_CHANNELS = ['effoyjobs', 'elelanajobs', 'freelance_ethio', 'hahujobs', 'ethiojobsofficial']

# --- ዳታቤዙን አንድ ጊዜ ብቻ ለማንበብ ---
def get_sent_jobs():
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            return [str(val.get('title')) for val in data.values()]
    except:
        pass
    return []

def save_to_firebase(text_snippet):
    try:
        requests.post(FIREBASE_URL, json={"title": text_snippet, "time": time.ctime()})
    except:
        pass

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # HTML Error ለመከላከል ልዩ ምልክቶችን ማጽዳት ወይም መጠቅለል
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"⚠️ Telegram Error: {res.text}")
    except:
        pass

async def run_telegram_scraper():
    if not STRING_SESSION:
        print("❌ Telegram Session አልተገኘም!")
        return
    
    sent_jobs_list = get_sent_jobs() # ዳታቤዙን እዚህ ጋር አንድ ጊዜ እናንብብ
    print(f"🚀 ስራ ተጀምሯል። {len(sent_jobs_list)} የቆዩ ስራዎች በዳታቤዝ አሉ።")

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.start()
    
    for channel in TARGET_CHANNELS:
        try:
            print(f"📡 @{channel} እየታየ ነው...")
            async for message in client.iter_messages(channel, limit=30): # ገደቡን ወደ 30 ከፍ አድርገነዋል
                if message.message:
                    msg_text = message.message
                    
                    if any(word.lower() in msg_text.lower() for word in IT_KEYWORDS):
                        # ለFirebase መለያ እንዲሆን የመጀመሪያ 60 ፊደላትን መውሰድ
                        snippet = msg_text[:60].replace("\n", " ").strip()
                        
                        if snippet not in sent_jobs_list:
                            # ጽሁፉን ማጽዳት (HTML Tags እንዳያበላሹ)
                            clean_text = msg_text.replace("<", "&lt;").replace(">", "&gt;")
                            # ሊንኮችን ማጽዳት ከፈለግክ re.sub መጠቀም ትችላለህ
                            
                            final_msg = f"<b>💻 አዲስ የ IT ስራ (@{channel})</b>\n\n{clean_text[:3800]}"
                            
                            send_to_telegram(final_msg)
                            save_to_firebase(snippet)
                            sent_jobs_list.append(snippet) # በዚሁ ዙር ድጋሚ እንዳይላክ
                            print(f"✅ ተላከ፡ {snippet[:30]}...")
                            await asyncio.sleep(2) # Telegram Flood እንዳያደርገን
        except Exception as e:
            print(f"❌ ስህተት በ @{channel}: {e}")
            
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_telegram_scraper())
