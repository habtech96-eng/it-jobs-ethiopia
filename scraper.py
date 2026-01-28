import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
TOKEN = "8250838814:AAF99sEJAEQ1_2O9-O0QnvCuDqWKUdEh45Y"
CHAT_ID = "-1003843080640"
# የአንተ Europe Server Firebase URL
FIREBASE_URL = "https://itjob-47561-default-rtdb.europe-west1.firebasedatabase.app/jobs.json"

# ለሙከራ ያህል ማንኛውንም ስራ እንዲያመጣ እነዚህን ቃላት ተጠቀም
KEYWORDS = ["and", "the", "job", "work", "Ethiopia", "አዲስ", "ስራ"]

def is_already_sent(title):
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                if data[key]['title'] == title:
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
    print("🚀 የሙከራ ፍለጋ ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # ለፍጥነት ያህል HahuJobsን ብቻ እንሞክር
    sources = ["https://hahujobs.net/jobs"]
    
    found_count = 0
    for url in sources:
        try:
            driver.get(url)
            time.sleep(10)
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                if len(title) > 5 and any(word.lower() in title.lower() for word in KEYWORDS):
                    if not is_already_sent(title) and href:
                        print(f"🎯 ተገኘ: {title}")
                        msg = f"<b>🧪 የሙከራ መልእክት</b>\n\n💼 <b>ስራ፡</b> {title}\n\n🔗 <a href='{href}'>ሊንክ</a>"
                        send_to_telegram(msg)
                        save_to_firebase(title)
                        found_count += 1
                        if found_count >= 5: break # ለሙከራ 5 ስራ ብቻ ይላክ
        except Exception as e:
            print(f"Error: {e}")
            
    driver.quit()
    print(f"🏁 ሙከራው ተጠናቋል! {found_count} ስራዎች ተልከዋል።")

if __name__ == "__main__":
    run_scraper()
