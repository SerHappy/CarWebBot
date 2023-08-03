from loguru import logger
from telethon.errors import BadRequestError
from telethon.errors import FloodWaitError
from telethon.errors import RPCError
from typing import Any
from typing import Callable

import time


def perform_action_with_retries(action: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Выполняет заданное действие с несколькими попытками в случае ошибок.

    Args:
        action (callable): Действие, которое следует выполнить.
        *args: Позиционные аргументы для действия.
        **kwargs: Именованные аргументы для действия.
    """
    max_attempts = 5
    attempt = 0
    logger.debug(f"Performing action {action} with args {args} and kwargs {kwargs}")
    while attempt < max_attempts:
        logger.debug(f"Attempt {attempt + 1} of {max_attempts}")
        try:
            return action(*args, **kwargs)
        except RPCError as e:
            if not handle_telegram_exception(e):
                break
        except Exception as e:
            logger.critical(f"Received unexpected error: {e}. Stopping...")
            break
        attempt += 1
    return None


def handle_telegram_exception(e: RPCError) -> bool:
    """
    Обрабатывает исключения, связанные с Telegram API.

    Args:
        e (RPCError): Исключение, которое нужно обработать.

    Returns:
        bool: Возвращает True, если исключение обработано и необходимо повторить попытку.
              Возвращает False, если обработка исключения не удалась.
    """
    if isinstance(e, FloodWaitError):
        retry_after = e.seconds + 1
        logger.warning(f"Received FloodWaitError from Telegram. Sleeping for {retry_after} seconds...")
        time.sleep(retry_after)
        logger.warning("Waking up and trying again...")
        return True
    elif isinstance(e, BadRequestError):
        logger.warning(f"Received BadRequestError from Telegram: {e}")
        return False
    else:
        logger.critical(f"Received unexpected error: {e}. Stopping...")
        return False
