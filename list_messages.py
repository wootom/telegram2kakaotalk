#!/usr/bin/env python3
"""Fetch recent messages from vaax notifier and display them."""

import asyncio
from telethon import TelegramClient
import config
import os

async def list_recent_messages():
    import os
    home_dir = os.path.expanduser("~")
    session_dir = os.path.join(home_dir, ".vaax-telegram")
    session_path = os.path.join(session_dir, 'vaax_session')
    
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    await client.start()
    
    # Find vaax notifier chat and get recent messages
    async for dialog in client.iter_dialogs():
        name = dialog.name or ''
        if 'vaax notifier' in name.lower():
            print(f"=== {name} ===\n")
            messages = await client.get_messages(dialog, limit=5)
            for i, msg in enumerate(messages):
                time_str = msg.date.strftime('%Y-%m-%d %H:%M:%S') if msg.date else 'Unknown'
                print(f"[{i+1}] {time_str}")
                print(f"{msg.text[:200] if msg.text else '(no text)'}...")
                print("-" * 50)
            break
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_recent_messages())
