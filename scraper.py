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
# የአንተ Firebase URL
FIREBASE_URL = "https://itjob-47561-default-rtdb.europe-west1.firebasedatabase.app/jobs.json"

# ፍለጋ የምናደርግባቸው ቃላት
KEYWORDS = ["Software", "Developer", "IT", "Computer Science", "Programming", "Network", "Database", "System", "Web", "Frontend", "Backend", "Full Stack", "Data", "Cyber", "Security", "App", "Mobile", "አይቲ", "ኮምፒውተር", "ሶፍትዌር"]

def is_already_sent(title):
    """Firebase ውስጥ ገብቶ ይህ ስራ በፊት ተልኮ እንደሆነ ያረጋግጣል"""
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        if data:
            # በዳታቤዙ ውስጥ ያለውን እያንዳንዱን ርዕስ ይፈትሻል
            for key in data:
                if data[key]['title'] == title:
                    return True
    except Exception as e:
        print(f"Firebase Check Error: {e}")
    return False

def save_to_firebase(title):
    """አዲስ የተገኘን ስራ ርዕስ Firebase ላይ ይመዘግባል"""
    try:
        requests.post(FIREBASE_URL, json={"title": title, "time": time.ctime()})
    except Exception as e:
        print(f"Firebase Save Error: {e}")

def send_to_telegram(text):
    """ወደ ቴሌግራም መልእክት ይልካል"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_scraper():
    print("🚀 ፍለጋ ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # የምንፈልግባቸው ድረ-ገጾች
    sources = [
        "https://hahujobs.net/jobs",
        "https://www.ethiojobs.net/search-results-jobs/?category%5B%5D=14&action=search",
        "https://www.2merkato.com/jobs/category/11-it-and-computer-science"
    ]
    
    found_new = 0
    for url in sources:
        try:
            print(f"🌐 በመክፈት ላይ: {url}")
            driver.get(url)
            time.sleep(15) # ገጹ እስኪጭን መጠበቅ
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                # ርዕሱ ከ 10 ፊደል በላይ ከሆነና IT ነክ ቃላት ካሉበት
                if len(title) > 10 and any(word.lower() in title.lower() for word in KEYWORDS):
                    if not is_already_sent(title) and href:
                        print(f"🎯 አዲስ ስራ ተገኘ: {title}")
                        msg = f"<b>🔥 አዲስ የ IT/Tech ስራ</b>\n\n👨‍💻 <b>ስራ፡</b> {title}\n\n🔗 <a href='{href}'>ዝርዝር መረጃና ማመልከቻ</a>"
                        send_to_telegram(msg)
                        save_to_firebase(title)
                        found_new += 1
        except Exception as e:
            print(f"❌ ስህተት በ {url}: {e}")
            
    print(f"🏁 ፍለጋ ተጠናቋል! {found_new} አዳዲስ ስራዎች ተልከዋል።")
    driver.quit()

if __name__ == "__main__":
    run_scraper()
