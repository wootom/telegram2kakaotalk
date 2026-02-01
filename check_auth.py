import asyncio
import os
from telethon import TelegramClient
import sys
sys.path.append('/Users/woojanghoon/vaax-telegram')
import config

async def main():
    # Use the absolute path to the session file in the home directory folder
    session_path = '/Users/woojanghoon/vaax-telegram/vaax_session'
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    await client.connect()
    is_auth = await client.is_user_authorized()
    print(f"Authorized Status: {is_auth}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
