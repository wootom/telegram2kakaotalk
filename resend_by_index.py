#!/usr/bin/env python3
"""Resend specific message by index."""

import asyncio
from telethon import TelegramClient
import config
from kakao_sender import send_to_kakao
import os
import sys

async def resend_message(index=1):
    import os
    home_dir = os.path.expanduser("~")
    session_dir = os.path.join(home_dir, ".vaax-telegram")
    session_path = os.path.join(session_dir, 'vaax_session')
    
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    await client.start()
    
    async for dialog in client.iter_dialogs():
        name = dialog.name or ''
        if 'vaax notifier' in name.lower():
            messages = await client.get_messages(dialog, limit=5)
            if index <= len(messages):
                msg = messages[index - 1]
                print(f"Sending message from {msg.date}:")
                print(f"{msg.text[:100]}...")
                if msg.text:
                    success = send_to_kakao(config.TARGET_KAKAO_ROOM, msg.text)
                    if success:
                        print("\n✅ Message sent to KakaoTalk!")
                    else:
                        print("\n❌ Failed to send to KakaoTalk")
            break
    
    await client.disconnect()

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    asyncio.run(resend_message(idx))
