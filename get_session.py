from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# ያንተን API_ID እና API_HASH እዚህ ጋር ተካ
API_ID = 31987639 
API_HASH = '1de0b58ba938bca8cd47d2292d6e5669'

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\nየአንተ STRING SESSION ኮድ ይህ ነው (በጥንቃቄ ቅዳው):\n")
    print(client.session.save())
