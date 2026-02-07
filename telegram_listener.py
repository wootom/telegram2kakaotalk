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

    # Listen for all messages (incoming and outgoing) to support 'Saved Messages' forwarding
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

        target_room = None
        
        # Load settings dynamically
        import json
        import os
        SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        
        settings = {"mappings": [], "recent_sources": []}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load settings.json: {e}")

        # Update recent sources if unique
        if source_name and source_name not in settings.get('recent_sources', []):
            try:
                # Keep only last 20 sources
                recents = [source_name] + settings.get('recent_sources', [])
                settings['recent_sources'] = recents[:20]
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"Failed to save recent sources: {e}")

        # Find ALL matching targets for multi-target broadcasting
        target_rooms = []
        
        # Check mappings in settings.json
        mappings = settings.get('mappings', [])
        for m in mappings:
            if m['source'].lower() in source_name.lower():
                target_rooms.append(m['target'])

        # Fallback to config.py if no mapping found (Backward Compatibility)
        if not target_rooms and hasattr(config, 'SOURCE_TO_TARGET_MAP'):
             for src_key, target_val in config.SOURCE_TO_TARGET_MAP.items():
                if src_key.lower() in source_name.lower():
                    target_rooms.append(target_val)
                    # Don't break here if we want to support 1:N in config.py too, 
                    # but config.py structure is 1:1 map, so break is fine or let it append if keys overlap.
        
        # Legacy fallback
        if not target_rooms and 'vaax notifier' in source_name.lower():
             target_rooms.append(getattr(config, 'TARGET_KAKAO_ROOM', 'VAAX'))

        # Remove duplicates
        target_rooms = list(set(target_rooms))

        if not target_rooms:
            logger.info(f"Skipping message from {source_name} (no target mapped)")
            return

        message_text = event.message.message
        
        if not message_text:
            return # Skip empty messages

        # Format message for KakaoTalk
        formatted_message = message_text
        
        logger.info(f"Broadcasting from '{source_name}' to {target_rooms}")
        
        encryption_errors = []
        success_count = 0
        
        for room in target_rooms:
            logger.info(f"Forwarding to '{room}'...")
            if send_to_kakao(room, formatted_message):
                success_count += 1
            else:
                logger.error(f"Failed to forward to '{room}'")

        if success_count > 0:
            logger.info(f"Message forwarded successfully to {success_count}/{len(target_rooms)} targets.")
        else:
            logger.error("Failed to forward message to any target.")

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
