import asyncio
import os
from telethon import TelegramClient
import sys

# Paths
SESSION_PATH = '/Users/woojanghoon/vaax-telegram/vaax_session'
API_ID = 31448443
API_HASH = 'dc8e3472e592ac6138b1bfb57e6e7d81'

async def main():
    print(f"Checking session at: {SESSION_PATH}.session")
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.connect()
    is_auth = await client.is_user_authorized()
    print(f"AUTHENTICATED: {is_auth}")
    if is_auth:
        me = await client.get_me()
        print(f"Logged in as: {me.first_name}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
