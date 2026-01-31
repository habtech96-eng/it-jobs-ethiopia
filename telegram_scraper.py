import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

# --- CONFIGURATION ---
# እነዚህን በ GitHub Secrets ውስጥ መመዝገብህን እንዳትረሳ
API_ID = 31987639 
API_HASH = '1de0b58ba938bca8cd47d2292d6e5669'
BOT_TOKEN = os.getenv("TG_TOKEN")
DESTINATION_CHANNEL = -1003843080640  # የአንተ ቻናል ID

# መረጃ እንዲመጣባቸው የምትፈልጋቸው ቻናሎች (username)
TARGET_CHANNELS = ['@ethiojobs', '@hahujobs', '@freelanceethiopia']

# የፍለጋ ቃላት
IT_KEYWORDS = ["software", "developer", "it ", "ict", "web", "computer", "network", "system", "data"]

client = TelegramClient('job_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def job_handler(event):
    message_text = event.message.message
    if not message_text:
        return

    # መልዕክቱ የ IT ስራ መሆኑን እናረጋግጥ
    if any(word.lower() in message_text.lower() for word in IT_KEYWORDS):
        print(f"🎯 አዲስ የ IT ስራ ተገኘ!")
        
        # ወደ አንተ ቻናል መልዕክቱን አስተላልፍ (Forward ወይም Copy)
        await client.send_message(DESTINATION_CHANNEL, message_text)

async def main():
    print("🚀 የቴሌግራም ቻናል ፍለጋ ተጀመረ...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
