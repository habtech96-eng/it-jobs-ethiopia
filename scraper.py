import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
TOKEN = "8250838814:AAF99sEJAEQ1_2O9-O0QnvCuDqWKUdEh45Y"
CHAT_ID = "-1003843080640"
FIREBASE_URL = "https://itjob-47561-default-rtdb.europe-west1.firebasedatabase.app/jobs.json"

# ለመፈለግ የምንጠቀምባቸው ቃላት
# --- ሰፊ የፍለጋ ቃላት (KEYWORDS) ---
KEYWORDS = [
    # አጠቃላይ የስራ ቃላት
    "job", "vacancy", "hiring", "career", "employment", "position", "work", "opportunity",
    "ስራ", "ክፍት", "ማስታወቂያ", "ቅጥር", "ሰራተኛ", "አዲስ",
    
    # የሙያ ዘርፎች (IT & Tech)
    "software", "developer", "it", "web", "computer", "network", "system", "data", "graphic",
    "programmer", "security", "database", "hardware", "support",
    
    # የሙያ ዘርፎች (ሌሎች)
    "accounting", "finance", "management", "manager", "marketing", "sales", "engineering", 
    "civil", "health", "nurse", "doctor", "teaching", "teacher", "driver", "bank", "banking",
    "human resource", "hr", "admin", "office", "clerk", "secretary",
    
    # ቦታዎች (ኢትዮጵያ ውስጥ)
    "ethiopia", "addis ababa", "adama", "hawassa", "bahir dar", "mekelle", "dire dawa",
    "አዲስ አበባ", "አዳማ", "ሀዋሳ", "ባህር ዳር", "ድሬዳዋ", "ጎንደር"
]

# 10 ድረ-ገጾች ዝርዝር
SOURCES = [
    "https://hahujobs.net/jobs",
    "https://www.ethiojobs.net",
    "https://www.ezega.com/Jobs/JobVacancies",
    "https://www.elelanajobs.com",
    "https://shegerjobs.net",
    "https://freelanceethiopia.com",
    "https://jobs.et",
    "https://www.tenderethiopia.com",
    "https://qefira.com/jobs",
    "https://dereja.com"
]

def is_already_sent(title):
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            for key in data:
                if data[key].get('title') == title:
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
    print(f"🚀 የ {len(SOURCES)} ድረ-ገጾች ፍለጋ ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    found_count = 0

    for url in SOURCES:
        print(f"🔎 በመፈለግ ላይ: {url}")
        try:
            driver.get(url)
            # ድረ-ገጹ እስኪከፈት 7 ሰከንድ ይጠብቃል
            time.sleep(7)
            
            # ሁሉንም ሊንኮች ይሰበስባል
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    title = link.text.strip()
                    href = link.get_attribute("href")
                    
                    if len(title) > 10 and any(word.lower() in title.lower() for word in KEYWORDS):
                        if not is_already_sent(title) and href:
                            print(f"🎯 አዲስ ስራ ተገኘ: {title}")
                            msg = f"<b>💼 አዲስ የስራ ማስታወቂያ</b>\n\n📌 <b>ርዕስ፡</b> {title}\n🌐 <b>ምንጭ፡</b> {url.split('/')[2]}\n\n🔗 <a href='{href}'>ዝርዝሩን እዚህ ይመልከቱ</a>"
                            send_to_telegram(msg)
                            save_to_firebase(title)
                            found_count += 1
                            
                            # በአንድ ዙር ከ 20 በላይ እንዳይልክ (Spam ለመከላከል)
                            if found_count >= 20: break 
                except: continue
        except Exception as e:
            print(f"❌ ስህተት ተከስቷል {url}: {e}")
            
    driver.quit()
    print(f"🏁 ፍለጋው ተጠናቋል! በአጠቃላይ {found_count} አዳዲስ ስራዎች ተልከዋል።")

if __name__ == "__main__":
    run_scraper()
