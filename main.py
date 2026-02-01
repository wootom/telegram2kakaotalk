import asyncio
import logging
from telegram_listener import start_listener
import config

if __name__ == "__main__":
    print("---------------------------------------------------")
    print("   Telegram to KakaoTalk Forwarder Started")
    print("---------------------------------------------------")
    
    if config.TARGET_KAKAO_ROOM == 'YOUR_KAKAO_ROOM_NAME':
        print("WARNING: TARGET_KAKAO_ROOM is not set in config.py.")
        print("Please edit config.py and set the target KakaoTalk room name.")
        exit(1)

    try:
        asyncio.run(start_listener())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
