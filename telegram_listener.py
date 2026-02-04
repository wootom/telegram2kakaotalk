from telethon import TelegramClient, events
import config
from kakao_sender import send_to_kakao
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_listener():
    """
    Starts the Telegram listener.
    """
    logger.info("Initializing Telegram Client...")
    
    if config.API_ID == 'YOUR_API_ID' or config.API_HASH == 'YOUR_API_HASH':
        logger.error("API_ID and API_HASH must be set in config.py")
        return

    import os
    import shutil
    
    # Define new session directory in user home
    home_dir = os.path.expanduser("~")
    session_dir = os.path.join(home_dir, ".vaax-telegram")
    
    # Create directory if it doesn't exist
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        logger.info(f"Created session directory: {session_dir}")

    base_path = os.path.dirname(os.path.abspath(__file__))
    
    if hasattr(config, 'BOT_TOKEN') and config.BOT_TOKEN:
        logger.info("Logging in with Bot Token...")
        session_name = 'vaax_bot_session'
        session_path = os.path.join(session_dir, session_name)
        client = TelegramClient(session_path, config.API_ID, config.API_HASH)
    else:
        logger.info("Logging in with User Account...")
        session_name = 'vaax_session'
        new_session_path = os.path.join(session_dir, session_name)
        
        # Check for old session file and migrate if needed
        old_session_path = os.path.join(base_path, session_name + '.session')
        if os.path.exists(old_session_path) and not os.path.exists(new_session_path + '.session'):
            logger.info(f"Migrating session file from {old_session_path} to {new_session_path}.session")
            try:
                shutil.move(old_session_path, new_session_path + '.session')
                logger.info("Migration successful.")
            except Exception as e:
                logger.error(f"Failed to migrate session file: {e}")
        
        logger.info(f"Using session file at: {new_session_path}.session")
        client = TelegramClient(new_session_path, config.API_ID, config.API_HASH)

    @client.on(events.NewMessage)
    async def handler(event):
        sender = await event.get_sender()
        chat = await event.get_chat()
        
        # Determine source name (User or Channel/Group title)
        source_name = getattr(chat, 'title', None)
        if not source_name:
            # If no title (private chat), try first_name + last_name
            first = getattr(sender, 'first_name', '') or ''
            last = getattr(sender, 'last_name', '') or ''
            if first or last:
                source_name = f"{first} {last}".strip()
            else:
                source_name = getattr(sender, 'username', 'Unknown')
        
        # Debug logging to help identify the correct filter
        logger.info(f"DEBUG: Chat Title: {getattr(chat, 'title', 'None')}")
        logger.info(f"DEBUG: Sender Username: {getattr(sender, 'username', 'None')}")
        logger.info(f"DEBUG: Sender Name: {getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}")
        logger.info(f"Resolved Source Name: {source_name}")

        if not source_name or 'vaax notifier' not in source_name.lower():
            logger.info(f"Skipping message from {source_name} (not vaax notifier)")
            return

        message_text = event.message.message
        
        if not message_text:
            return # Skip empty messages (e.g. media only, though Telethon usually gives text for media captions)

        # Format message for KakaoTalk (no prefix, just the message)
        formatted_message = message_text
        
        logger.info(f"Forwarding to KakaoTalk: {config.TARGET_KAKAO_ROOM}")
        success = send_to_kakao(config.TARGET_KAKAO_ROOM, formatted_message)
        
        if success:
            logger.info("Message forwarded successfully.")
        else:
            logger.error("Failed to forward message.")

    try:
        logger.info("Starting Telegram listener Loop...")
        if hasattr(config, 'BOT_TOKEN') and config.BOT_TOKEN:
            await client.start(bot_token=config.BOT_TOKEN)
        else:
            await client.start()
        
        logger.info("Telegram Client started successfully. Running until disconnected...")
        # Run until disconnected
        await client.run_until_disconnected()
        logger.info("Telegram Client disconnected unexpectedly.")
    except Exception as e:
        logger.error(f"Error in listener loop: {e}", exc_info=True)
    finally:
        await client.disconnect()
        logger.info("Telegram Client clean up done.")
