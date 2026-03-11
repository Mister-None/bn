from telethon import TelegramClient, events, functions, types, errors, Button
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.users import GetFullUserRequest
from dotenv import load_dotenv
import os, asyncio, sys

load_dotenv()

TG_BOT_TOKEN = os.getenv('tg_bot_token')
APP_ID = os.getenv('app_id') 
APP_HASH = os.getenv('app_hash')
TG_BOT_SESSION = os.getenv('tg_bot_session')
TG_USER_ID = os.getenv('tg_user_id')

client = TelegramClient(TG_BOT_SESSION, APP_ID, APP_HASH)

message = sys.argv[1]

async def main():
    await client.start(bot_token=TG_BOT_TOKEN)
    await client.send_message(TG_USER_ID, message)

asyncio.run(main())

