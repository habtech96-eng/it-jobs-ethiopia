import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = "8250838814:AAF99sEJAEQ1_2O9-O0QnvCuDqWKUdEh45Y"
DESTINATION_CHANNEL = -1003843080640 
DB_FILE = "sent_jobs.txt"

KEYWORDS = ["Software", "Developer", "IT ", "Computer Science", "Information Technology", "Network", "Database", "Programming", "System Admin", "Web Design", "Graphics", "Hardware", "Full Stack", "Frontend", "Backend", "Data Science", "Cyber", "Security", "App Development", "Mobile", "UI/UX", "አይቲ", "ኮምፒውተር", "ሶፍትዌር"]

# የማይፈለጉ ቃላት (እነዚህ ካሉ ቦቱ አይልከውም)
EXCLUDE_WORDS = ["how to", "faq", "sign in", "login", "register", "about us", "contact", "policy", "terms", "help"]

JOB_SOURCES = [
    "https://hahujobs.net/jobs",
    "https://www.ethiojobs.net",
    "https://www.employethiopia.com",
    "https://www.2merkato.com/jobs",
    "https://www.dereja.com/jobs"
]

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": DESTINATION_CHANNEL, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

def is_already_sent(title):
    if not os.path.exists(DB_FILE): return False
    with open(DB_FILE, "r", encoding="utf-8") as f: return title in f.read()

def save_to_db(title):
    with open(DB_FILE, "a", encoding="utf-8") as f: f.write(title + "\n")

def run_mega_job_scraper():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    found_new = 0
    for url in JOB_SOURCES:
        try:
            driver.get(url)
            time.sleep(10)
            elements = driver.find_elements(By.TAG_NAME, "a")
            for el in elements:
                title = el.text.strip()
                href = el.get_attribute("href")
                
                # 1. የ IT ቃላት መኖራቸውን ማረጋገጥ
                if len(title) > 15 and any(word.lower() in title.lower() for word in KEYWORDS):
                    # 2. የማይረቡ ቃላት (FAQ, How to) አለመኖራቸውን ማረጋገጥ
                    if not any(ex.lower() in title.lower() for ex in EXCLUDE_WORDS):
                        if not is_already_sent(title) and href:
                            site = url.split(".")[1].upper()
                            msg = f"<b>🔥 አዲስ የ IT/Tech ስራ ተገኝቷል</b>\n\n👨‍💻 <b>ስራ፡</b> {title}\n🏢 <b>ምንጭ፡</b> {site}\n\n🔗 <a href='{href}'>ዝርዝር መረጃና ማመልከቻ</a>"
                            send_to_telegram(msg)
                            save_to_db(title)
                            found_new += 1
        except: continue
    driver.quit()

if __name__ == "__main__":
    run_mega_job_scraper()
