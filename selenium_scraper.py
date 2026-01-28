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

# ቃላቶቹን አሻሽለናል
KEYWORDS = ["Software", "Developer", "IT", "Computer", "Technology", "Network", "Database", "Programming", "System", "Web", "Graphics", "Hardware", "Full Stack", "Data", "Cyber", "Security", "App", "Mobile", "UI/UX", "አይቲ", "ኮምፒውተር", "ሶፍትዌር", "ስራ"]

EXCLUDE_WORDS = ["how to", "faq", "sign in", "login", "register", "about us", "contact", "policy", "terms", "help", "feedback"]

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
    with open(DB_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        return title in content

def save_to_db(title):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

def run_mega_job_scraper():
    print("🚀 ፍለጋ ተጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    found_count = 0
    for url in JOB_SOURCES:
        try:
            print(f"🔍 {url} እየታየ ነው...")
            driver.get(url)
            time.sleep(12) # ድረ-ገጹ እስኪከፈት ትንሽ እንታገስ
            elements = driver.find_elements(By.TAG_NAME, "a")
            
            for el in elements:
                title = el.text.strip()
                href = el.get_attribute("href")
                
                if len(title) > 10 and any(word.lower() in title.lower() for word in KEYWORDS):
                    if not any(ex.lower() in title.lower() for ex in EXCLUDE_WORDS):
                        if not is_already_sent(title) and href:
                            print(f"✅ አዲስ ስራ ተገኘ: {title}")
                            site = url.split(".")[1].upper()
                            msg = f"<b>🔥 አዲስ የ IT/Tech ስራ ተገኝቷል</b>\n\n👨‍💻 <b>ስራ፡</b> {title}\n🏢 <b>ምንጭ፡</b> {site}\n\n🔗 <a href='{href}'>ዝርዝር መረጃና ማመልከቻ</a>"
                            send_to_telegram(msg)
                            save_to_db(title)
                            found_count += 1
        except Exception as e:
            print(f"❌ ስህተት በ {url}: {e}")
            continue
            
    print(f"🏁 ፍለጋ ተጠናቋል! {found_count} አዳዲስ ስራዎች ተልከዋል።")
    driver.quit()

if __name__ == "__main__":
    run_mega_job_scraper()
