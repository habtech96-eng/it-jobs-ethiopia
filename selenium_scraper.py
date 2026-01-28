import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TOKEN = "8250838814:AAF99sEJAEQ1_2O9-O0QnvCuDqWKUdEh45Y"
DESTINATION_CHANNEL = -1003843080640 
DB_FILE = "sent_jobs.txt"

# ቃላቶቹን በጣም ሰፊ አድርገናቸዋል
KEYWORDS = ["Software", "Developer", "IT", "Computer", "Technology", "Network", "Database", "System", "Web", "Graphics", "Data", "Security", "App", "አይቲ", "ኮምፒውተር", "ሶፍትዌር"]

JOB_SOURCES = [
    "https://hahujobs.net/jobs",
    "https://www.ethiojobs.net/search-results-jobs/?searchId=1706473653.8648&action=search", # ቀጥታ የ IT ፍለጋ ሊንክ
    "https://www.dereja.com/jobs",
    "https://www.employethiopia.com/jobs-in-ethiopia"
]

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": DESTINATION_CHANNEL, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

def is_already_sent(title):
    if not os.path.exists(DB_FILE): return False
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return title.strip() in f.read()

def save_to_db(title):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")

def run_mega_job_scraper():
    print("🚀 Deep Scanning Started...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    found_count = 0
    for url in JOB_SOURCES:
        try:
            print(f"🌐 Opening: {url}")
            driver.get(url)
            
            # ገጹ እስኪጭን 20 ሰከንድ እንጠብቅ (Wait for elements to load)
            time.sleep(20)
            
            # ሁሉንም ሊንኮች እና ርዕሶች መፈለግ
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"🔎 Found {len(links)} links on page.")

            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                if len(title) > 8 and any(word.lower() in title.lower() for word in KEYWORDS):
                    if not is_already_sent(title) and href:
                        print(f"🎯 Match Found: {title}")
                        site = url.split(".")[1].upper()
                        msg = f"<b>🔥 አዲስ የ IT ስራ</b>\n\n👨‍💻 <b>ስራ፡</b> {title}\n🏢 <b>ምንጭ፡</b> {site}\n\n🔗 <a href='{href}'>ዝርዝር መረጃ</a>"
                        send_to_telegram(msg)
                        save_to_db(title)
                        found_count += 1
                        time.sleep(1) # Telegram እንዳይዘጋን
        except Exception as e:
            print(f"❌ Error on {url}: {e}")
            
    print(f"🏁 Done! Found {found_count} jobs.")
    driver.quit()

if __name__ == "__main__":
    run_mega_job_scraper()
