from django.conf import settings
from loguru import logger
from telethon.sync import TelegramClient
from typing import Any

import asyncio
import concurrent.futures


def fetch_telegram_client() -> TelegramClient:
    """Возвращает клиента Telegram, заданного в env файле."""
    return TelegramClient(
        session=settings.TELETHON_SESSION_NAME,
        api_id=settings.TELETHON_API_ID,
        api_hash=settings.TELETHON_API_HASH,
        system_version=settings.TELETHON_SYSTEM_VERSION,
    )


def run_in_new_thread(func, *args, **kwargs) -> Any:
    """Запускает функцию `func` в отдельном потоке."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        concurrent.futures.wait([future])
        _check_future_status(future)
        return future.result()


def _check_future_status(future: concurrent.futures.Future) -> None:
    """Проверяет статус задачи `future`, запущенной в отдельном потоке."""
    if future.cancelled():
        logger.error("Task was cancelled")
        return

    if future.done():
        try:
            future.result()
        except Exception as e:
            logger.error(f"Task ended with an error: {e}")
            return
        else:
            logger.info("Task ended successfully")
            return

    if future.running():
        logger.info("Task is running")
        return


def set_new_event_loop() -> None:
    """Создает новый event loop для asyncio."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
