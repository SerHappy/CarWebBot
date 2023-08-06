from django.conf import settings
from telethon.sync import TelegramClient


with TelegramClient(
    session=settings.TELETHON_SESSION_NAME,
    api_id=settings.TELETHON_API_ID,
    api_hash=settings.TELETHON_API_HASH,
    system_version=settings.TELETHON_SYSTEM_VERSION,
) as client:
    client: TelegramClient
    try:
        print("Success!")
        print(client.get_me().stringify())
    except Exception as e:
        print("Error!")
        print(e)
