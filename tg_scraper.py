import os
import re
import time
import requests
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- CONFIGURATION (ከ GitHub Secrets የሚመጡ) ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
API_ID = int(os.getenv("API_ID")) if os.getenv("API_ID") else None
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION")
FIREBASE_URL = os.getenv("FIREBASE_URL")

# Firebase URL መጨረሻው .json መሆኑን ማረጋገጥ
if FIREBASE_URL and not FIREBASE_URL.endswith(".json"):
    FIREBASE_URL += ".json"

# የምንፈልጋቸው የሙያ ቃላት
IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data", "graphic", "programmer"]

# የምንሰልላቸው ቻናሎች
TARGET_CHANNELS = ['effoyjobs', 'elelanajobs', 'freelance_ethio', 'hahujobs', 'ethiojobsofficial']

def is_already_sent(text_snippet):
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                if data[key].get('title') == text_snippet: return True
    except: pass
    return False

def save_to_firebase(text_snippet):
    try: requests.post(FIREBASE_URL, json={"title": text_snippet, "time": time.ctime()})
    except: pass

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

async def run_telegram_scraper():
    if not STRING_SESSION:
        print("❌ Telegram Session አልተገኘም!")
        return
    
    print("🚀 Telegram Scraper ስራ ጀመረ...")
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.start()
    
    for channel in TARGET_CHANNELS:
        try:
            print(f"📡 @{channel} እየታየ ነው...")
            # በእያንዳንዱ ቻናል የመጨረሻዎቹን 15 መልእክቶች ያያል
            async for message in client.iter_messages(channel, limit=15):
                if message.message:
                    msg_text = message.message
                    # የ IT ቃላት መኖራቸውን ማረጋገጥ
                    if any(word.lower() in msg_text.lower() for word in IT_KEYWORDS):
                        # ለFirebase መለያ እንዲሆን የመጀመሪያ 50 ፊደላትን መውሰድ
                        snippet = msg_text[:60].replace("\n", " ")
                        
                        if not is_already_sent(snippet):
                            # ሊንኮችን እና አላስፈላጊ @ ምልክቶችን ማጽዳት
                            clean_text = re.sub(r'http\S+|www\S+|@\w+', '', msg_text).strip()
                            
                            final_msg = f"<b>💻 አዲስ የ IT ስራ (ከቴሌግራም @{channel})</b>\n\n{clean_text[:3500]}" # የቴሌግራም የፊደል ገደብን ለመጠበቅ
                            
                            send_to_telegram(final_msg)
                            save_to_firebase(snippet)
                            print(f"✅ አዲስ ስራ ተላከ፡ {snippet[:30]}...")
        except Exception as e:
            print(f"❌ ስህተት በ @{channel}: {e}")
            
    await client.disconnect()
    print("✅ የቴሌግራም ስካኒንግ ተጠናቋል።")

if __name__ == "__main__":
    asyncio.run(run_telegram_scraper())
