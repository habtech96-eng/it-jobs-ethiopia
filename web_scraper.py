import os
import time
import requests
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configurations
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
FIREBASE_URL = os.getenv("FIREBASE_URL")
if FIREBASE_URL and not FIREBASE_URL.endswith(".json"): FIREBASE_URL += ".json"

IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data", "graphic", "programmer"]
SOURCES = ["https://hahujobs.net/jobs", "https://www.ethiojobs.net", "https://www.elelanajobs.com", "https://www.ezega.com/Jobs/JobVacancies"]

def is_already_sent(title):
    try:
        data = requests.get(FIREBASE_URL).json()
        if data:
            for key in data:
                if data[key].get('title').strip().lower() == title.strip().lower(): return True
    except: pass
    return False

async def run_web_scraper():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    for url in SOURCES:
        try:
            driver.get(url)
            await asyncio.sleep(7)
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                if len(title) > 10 and any(word in title.lower() for word in IT_KEYWORDS):
                    if not is_already_sent(title):
                        source = url.split('/')[2].replace('www.', '')
                        msg = f"<b>💻 የድረ-ገጽ ስራ፡</b> {title}\n🔗 <a href='{href}'>ሊንክ</a>"
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
                        requests.post(FIREBASE_URL, json={"title": title, "time": time.ctime()})
        except Exception as e: print(f"Error: {e}")
    driver.quit()

if __name__ == "__main__":
    asyncio.run(run_web_scraper())
