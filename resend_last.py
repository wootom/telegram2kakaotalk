#!/usr/bin/env python3
"""Fetch and resend the last message from vaax notifier to KakaoTalk."""

import asyncio
from telethon import TelegramClient
import config
from kakao_sender import send_to_kakao
import os

async def resend_last_message():
    import os
    home_dir = os.path.expanduser("~")
    session_dir = os.path.join(home_dir, ".vaax-telegram")
    session_path = os.path.join(session_dir, 'vaax_session')
    
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    await client.start()
    
    # Find vaax notifier chat and get last message
    async for dialog in client.iter_dialogs():
        name = dialog.name or ''
        if 'vaax notifier' in name.lower():
            print(f"Found: {name}")
            messages = await client.get_messages(dialog, limit=1)
            if messages:
                msg = messages[0]
                print(f"Last message: {msg.text}")
                if msg.text:
                    success = send_to_kakao(config.TARGET_KAKAO_ROOM, msg.text)
                    if success:
                        print("Message sent to KakaoTalk!")
                    else:
                        print("Failed to send to KakaoTalk")
            break
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(resend_last_message())
