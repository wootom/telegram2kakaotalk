import asyncio
from telethon import TelegramClient
import config
import os

async def main():
    # Force the path to be absolute to avoid any confusion
    base_path = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(base_path, 'vaax_session')
    
    print(f"세션 파일 확인 중: {session_path}.session")
    
    client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    
    await client.connect()
    
    authorized = await client.is_user_authorized()
    
    if not authorized:
        print("로그인이 필요합니다. 전화번호 인증을 진행해 주세요.")
        # This will trigger the interactive login if needed
        await client.start()
        print("로그인 성공!")
    else:
        me = await client.get_me()
        print(f"이미 로그인되어 있습니다: {me.first_name} ({me.id})")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
