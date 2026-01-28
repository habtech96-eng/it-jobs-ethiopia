import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- መረጃዎች ---
TOKEN = "8250838814:AAF99sEJAEQ1_2O9-O0QnvCuDqWKUdEh45Y"
CHAT_ID = "-1003843080640"

def test_telegram():
    print("📡 ቴሌግራምን በመሞከር ላይ...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": "🤖 ቦቱ በይፋ ስራ ጀምሯል!"})
    print(f"Telegram Test Status: {r.status_code}")

def run_scraper():
    print("🚀 ቦቱ ድረ-ገጾችን መፈተሽ ጀመረ...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # አንድ ድረ-ገጽ ብቻ ለሙከራ
    test_url = "https://hahujobs.net/jobs"
    print(f"🌐 በመክፈት ላይ: {test_url}")
    driver.get(test_url)
    time.sleep(10)
    
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"✅ በገጹ ላይ {len(links)} ሊንኮች ተገኝተዋል!")
    
    for link in links[:20]: # የመጀመሪያዎቹን 20 ብቻ መፈተሽ
        title = link.text.strip()
        if title:
            print(f"🔗 የታየ ስራ: {title}")
            # ማንኛውንም ስራ ለሙከራ ይላክ
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": f"ሙከራ: {title}"})
            break # አንድ ካገኘህ ይብቃን ለሙከራ
            
    driver.quit()

if __name__ == "__main__":
    test_telegram()
    run_scraper()
