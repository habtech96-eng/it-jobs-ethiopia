import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
FIREBASE_URL = os.getenv("FB_URL")

# IT Keywords (ትክክለኛ ስራዎችን ለመለየት)
IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", 
               "system", "data", "graphic", "programmer", "security", "database", 
               "hardware", "support", "coding", "technician", "information technology"]

# አላስፈላጊ ቃላት (እነዚህን የያዘ ሊንክ ችላ ይባላል)
EXCLUDE_WORDS = ["login", "register", "apply", "details", "contact", "about", "services", "home", "search"]

SOURCES = [
    "https://hahujobs.net/jobs",
    "https://www.ethiojobs.net",
    "https://www.elelanajobs.com",
    "https://www.ezega.com/Jobs/JobVacancies",
    "https://shegerjobs.net",
    "https://www.tenderethiopia.com/category/jobs",
    "https://jobs.et",
    "https://freelanceethiopia.com",
    "https://qefira.com/jobs",
    "https://dereja.com"
]

def is_already_sent(title):
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                if data[key].get('title').strip().lower() == title.strip().lower():
                    return True
    except: pass
    return False

def save_to_firebase(title):
    try:
        requests.post(FIREBASE_URL, json={"title": title, "time": time.ctime()})
    except: pass

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

def run_scraper():
    print(f"🚀 ፍለጋ ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    found_count = 0
    for url in SOURCES:
        try:
            print(f"🔎 በመፈለግ ላይ: {url}")
            driver.get(url)
            time.sleep(7) 
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                # 1. ርዕሱ ባዶ ካልሆነ እና ከ 10 ፊደል በላይ ከሆነ
                if len(title) > 10:
                    title_low = title.lower()
                    
                    # 2. የ IT ቃላት ካሉበት እና አላስፈላጊ ቃላት (Apply/Login) ከሌሉበት
                    is_it_job = any(word in title_low for word in IT_KEYWORDS)
                    is_garbage = any(word in title_low for word in EXCLUDE_WORDS)
                    
                    if is_it_job and not is_garbage:
                        if not is_already_sent(title) and href:
                            source_name = url.split('/')[2].replace('www.', '')
                            msg = f"<b>💻 አዲስ የ IT ስራ</b>\n\n💼 <b>ስራ፡</b> {title}\n🌐 <b>ምንጭ፡</b> {source_name}\n\n🔗 <a href='{href}'>ዝርዝሩን እዚህ ይመልከቱ</a>"
                            
                            send_to_telegram(msg)
                            save_to_firebase(title)
                            found_count += 1
                            time.sleep(1)
        except Exception as e:
            print(f"❌ ስህተት: {e}")
            
    driver.quit()
    print(f"🏁 ተጠናቋል! {found_count} አዳዲስ ስራዎች ተልከዋል።")

if __name__ == "__main__":
    run_scraper()
