import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



# Keywords - "System" የሚለውን አውጥተነዋል (FAQ እንዳያመጣ)
KEYWORDS = ["Software", "Developer", "Computer Science", "Information Technology", "Network", "Database", "Programming", "Web Design", "Frontend", "Backend", "Full Stack", "Cyber", "Security", "አይቲ", "ሶፍትዌር"]

# በጭራሽ መላክ የሌለባቸው ቃላት (Blacklist)
BLACKLIST = ["easy apply", "how to", "faq", "edit my cv", "sign in", "login", "hospital", "furniture", "supervisor", "apply for a job"]

JOB_SOURCES = [
    "https://hahujobs.net/jobs",
    "https://www.ethiojobs.net/search-results-jobs/?category%5B%5D=14&action=search", # ቀጥታ የ IT Category
    "https://www.2merkato.com/jobs/category/11-it-and-computer-science",
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(90) # ለዘገምተኛ ድረ-ገጾች ጊዜ መስጠት
    
    found_count = 0
    for url in JOB_SOURCES:
        try:
            print(f"🌐 በመክፈት ላይ: {url}")
            driver.get(url)
            time.sleep(15) # ገጹ እስኪጭን መጠበቅ
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                # የማጣሪያ ህግ (Logic)
                if len(title) > 12 and any(word.lower() in title.lower() for word in KEYWORDS):
                    # ብላክሊስት ውስጥ ካለ አትላክ
                    if not any(bad.lower() in title.lower() for bad in BLACKLIST):
                        if not is_already_sent(title) and href:
                            print(f"🎯 ተገኘ: {title}")
                            msg = f"<b>🔥 አዲስ የ IT/Tech ስራ</b>\n\n👨‍💻 <b>ስራ፡</b> {title}\n\n🔗 <a href='{href}'>ዝርዝር መረጃና ማመልከቻ</a>"
                            send_to_telegram(msg)
                            save_to_db(title)
                            found_count += 1
        except Exception as e:
            print(f"❌ ስህተት በ {url}: {e}")
            
    print(f"🏁 ተጠናቀቀ! {found_count} ስራዎች ተልከዋል።")
    driver.quit()

if __name__ == "__main__":
    run_mega_job_scraper()
