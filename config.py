# Telegram API Credentials
# Get these from https://my.telegram.org
API_ID = 31448443
API_HASH = 'dc8e3472e592ac6138b1bfb57e6e7d81'

# Bot Token (Optional)
# IMPORTANT: To receive messages FROM a bot, we must login as a USER, not as the bot itself.
# So we comment this out.
# BOT_TOKEN = '8526353326:AAGuYBDDyOiZfQd4hbpHyIwGzvFK0_Bzqa4'

# KakaoTalk Settings
# Mapping: 'Telegram Source Name' -> 'KakaoTalk Room Name'
# IMPORTANT: The target rooms must be OPEN on your screen.
SOURCE_TO_TARGET_MAP = {
    'vaax notifier': 'VAAX',
    'Openclaw-fovea': 'FOVEA',
    '포비아': 'FOVEA'
}

# Legacy support (will be deprecated)
TARGET_KAKAO_ROOM = 'VAAX'

# Source Telegram Chats (Optional)
# List of chat IDs or usernames to forward from. Leave empty to forward ALL messages (not recommended).
# Example: ['@my_channel', 123456789]
SOURCE_TELEGRAM_CHATS = []
