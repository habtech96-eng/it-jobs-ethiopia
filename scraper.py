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
FIREBASE_URL = "https://itjob-47561-default-rtdb.europe-west1.firebasedatabase.app/jobs.json"

# IT Keywords
IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", 
               "system", "data", "graphic", "programmer", "security", "database", 
               "hardware", "support", "coding", "technician", "information technology"]

# 10+ የኢትዮጵያ ስራ ድረ-ገጾች ዝርዝር
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
    """Firebase ውስጥ ርዕሱ ካለ True ይመልሳል"""
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                # ርዕሱን በትክክል ለማነጻጸር Spaces እና Case እናስተካክላለን
                if data[key].get('title').strip().lower() == title.strip().lower():
                    return True
    except: pass
    return False

def save_to_firebase(title):
    """አዲስ ስራ ሲገኝ Firebase ላይ ይመዘግባል"""
    try:
        requests.post(FIREBASE_URL, json={"title": title, "time": time.ctime()})
    except: pass

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

def run_scraper():
    print(f"🚀 የ {len(SOURCES)} ድረ-ገጾች ፍለጋ ተጀመረ...")
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
            time.sleep(8) # ድረ-ገጹ እስኪጭን መጠበቅ
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                # 1. ርዝመትና IT መሆኑን ቼክ ያደርጋል
                if len(title) > 10 and any(word.lower() in title.lower() for word in IT_KEYWORDS):
                    # 2. ከዚህ በፊት ያልተላከ መሆኑን ያረጋግጣል
                    if not is_already_sent(title) and href:
                        print(f"🎯 አዲስ IT ስራ ተገኘ: {title}")
                        source_name = url.split('/')[2].replace('www.', '')
                        msg = f"<b>💻 አዲስ የ IT ስራ</b>\n\n💼 <b>ስራ፡</b> {title}\n🌐 <b>ምንጭ፡</b> {source_name}\n\n🔗 <a href='{href}'>ዝርዝሩን እዚህ ይመልከቱ</a>"
                        
                        send_to_telegram(msg)
                        save_to_firebase(title)
                        found_count += 1
                        time.sleep(2) # ቴሌግራም እንዳያግደን ትንሽ መጠበቅ
        except Exception as e:
            print(f"❌ ስህተት በ {url}: {e}")
            
    driver.quit()
    print(f"🏁 ፍለጋው ተጠናቋል! {found_count} አዳዲስ IT ስራዎች ተልከዋል።")

if __name__ == "__main__":
    run_scraper()