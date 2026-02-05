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

# --- ዳታቤዙን ለማንበብ (Timeout ተጨምሯል) ---
def get_sent_jobs():
    try:
        # ለ 15 ሰከንድ ብቻ ይጠብቃል፤ ካልመለሰ ይተወዋል
        response = requests.get(FIREBASE_URL, timeout=15)
        data = response.json()
        if data:
            return [str(val.get('title')) for val in data.values()]
    except Exception as e:
        print(f"⚠️ Firebase Reading Error: {e}")
    return []

# --- ዳታቤዝ ላይ ለመጻፍ (Timeout ተጨምሯል) ---
def save_to_firebase(text_snippet):
    try:
        requests.post(FIREBASE_URL, json={"title": text_snippet, "time": time.ctime()}, timeout=15)
    except Exception as e:
        print(f"⚠️ Firebase Writing Error: {e}")

# --- ቴሌግራም ለመላክ ---
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        res = requests.post(url, data=payload, timeout=20)
        if res.status_code == 429: # Too Many Requests
            print("⚠️ Telegram is rate-limiting us. Sleeping...")
            time.sleep(30) # ለ 30 ሰከንድ እረፍት
        elif res.status_code != 200:
            print(f"⚠️ Telegram Error: {res.text}")
    except Exception as e:
        print(f"⚠️ Connection Error to Telegram: {e}")

async def run_telegram_scraper():
    if not STRING_SESSION:
        print("❌ Telegram Session አልተገኘም!")
        return
    
    # መጀመሪያ ዳታቤዙን እናንብብ
    sent_jobs_list = get_sent_jobs()
    print(f"🚀 ስራ ተጀምሯል። {len(sent_jobs_list)} የቆዩ ስራዎች አሉ።")

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    
    try:
        # ግንኙነቱ ካልተሳካ ለ 30 ሰከንድ ብቻ እንዲሞክር (Infinite loop ይከላከላል)
        await asyncio.wait_for(client.start(), timeout=30)
    except asyncio.TimeoutError:
        print("❌ Telegram Client Start Timeout!")
        return

    for channel in TARGET_CHANNELS:
        try:
            print(f"📡 @{channel} እየታየ ነው...")
            # limit=20 ለ GitHub Actions የበለጠ አስተማማኝ ነው
            async for message in client.iter_messages(channel, limit=20): 
                if message.message:
                    msg_text = message.message
                    
                    if any(word.lower() in msg_text.lower() for word in IT_KEYWORDS):
                        snippet = msg_text[:60].replace("\n", " ").strip()
                        
                        if snippet not in sent_jobs_list:
                            clean_text = msg_text.replace("<", "&lt;").replace(">", "&gt;")
                            final_msg = f"<b>💻 አዲስ የ IT ስራ (@{channel})</b>\n\n{clean_text[:3800]}"
                            
                            send_to_telegram(final_msg)
                            save_to_firebase(snippet)
                            sent_jobs_list.append(snippet)
                            print(f"✅ ተላከ፡ {snippet[:30]}...")
                            await asyncio.sleep(3) # እረፍቱን ወደ 3 ሰከንድ ከፍ አድርገነዋል
            
            # በእያንዳንዱ ቻናል መካከል እረፍት መስጠት (Rate limit ይከላከላል)
            await asyncio.sleep(5) 
            
        except Exception as e:
            print(f"❌ ስህተት በ @{channel}: {e}")
            
    await client.disconnect()
    print("🏁 Scanning ተጠናቋል።")

if __name__ == "__main__":
    # አጠቃላይ ስራው ከ 10 ደቂቃ በላይ እንዲፈጅ አንፈልግም
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait_for(run_telegram_scraper(), timeout=600))
    except asyncio.TimeoutError:
        print("❌ Global Timeout: ስራው በጣም ስለረዘመ ተቋርጧል።")
