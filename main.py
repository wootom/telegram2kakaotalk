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
        # exit(1) # We can continue as we use settings.json now

    # Start Web Admin
    import threading
    import web_admin
    threading.Thread(target=web_admin.run_admin_server, daemon=True).start()
    print("🌍 Web Admin running at http://127.0.0.1:5001")

    try:
        asyncio.run(start_listener())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
