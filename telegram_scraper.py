import os
import re
import asyncio
from telethon import TelegramClient, events

# --- CONFIGURATION ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
DESTINATION_CHANNEL = -1003843080640

# የአንተ ቻናሎች ዝርዝር
TARGET_CHANNELS = [
    'effoyjobs', 'elelanajobs', 'freelance_ethio', 
    'hahujobs', 'googlejobsinamhara1', 'ethiojobsofficial',
    'ethiojobs', 'freelanceethiopia'
]

IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data"]

# ጽሁፉን ለማጽዳት የሚጠቅም Function
def clean_job_text(text):
    # 1. ሌሎች የቴሌግራም ሊንኮችን እና @username ማጥፊያ
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    
    # 2. አላስፈላጊ ቃላትን ማጥፊያ (ማስታወቂያዎች)
    garbage_phrases = [
        "Join our channel", "በዚህ ሊንክ ይመዝገቡ", "Share with your friends",
        "ለተጨማሪ ስራዎች", "Contact us", "Click here"
    ]
    for phrase in garbage_phrases:
        text = text.replace(phrase, "")
        
    return text.strip()

client = TelegramClient('job_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def job_handler(event):
    message_text = event.message.message
    if not message_text:
        return

    # የ IT ስራ መሆኑን ቼክ ማድረግ
    if any(word.lower() in message_text.lower() for word in IT_KEYWORDS):
        print(f"🎯 ትኩስ የ IT ስራ ተገኘ!")
        
        # ጽሁፉን አጽዳው
        clean_text = clean_job_text(message_text)
        
        # መልዕክቱን አሳምረህ አዘጋጀው
        final_msg = f"<b>💻 አዲስ የ IT ስራ (ከቴሌግራም የተገኘ)</b>\n\n{clean_text}\n\n✅ <i>በጥንቃቄ ያመልክቱ!</i>"
        
        await client.send_message(DESTINATION_CHANNEL, final_msg, parse_mode='html')

async def main():
    print("🚀 የቴሌግራም ስክራፐር በንቃት እየፈለገ ነው...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
