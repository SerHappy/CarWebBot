from loguru import logger
from telebot.apihelper import ApiTelegramException
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
        try:
            return action(*args, **kwargs)
        except ApiTelegramException as e:
            if not handle_telegram_exception(e):
                break
        attempt += 1
    return None


def handle_telegram_exception(e: ApiTelegramException) -> bool:
    """
    Обрабатывает исключения, связанные с Telegram API.

    Args:
        e (ApiTelegramException): Исключение, которое нужно обработать.

    Returns:
        bool: Возвращает True, если исключение обработано и необходимо повторить попытку.
              Возвращает False, если обработка исключения не удалась.
    """
    if e.error_code == 429:
        retry_after = int(e.description.split(" ")[-1]) + 1
        logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
        time.sleep(retry_after)
        logger.warning("Waking up and trying again...")
        return True
    if e.error_code == 400:
        logger.warning(f"Received 400 error from Telegram. Error message: {e.description}")
        return False
    if e.error_code == 502:
        logger.warning(f"Received 502 error from Telegram. Error message: {e.description}")
        time.sleep(1)
        return True
    else:
        logger.critical(f"Error is not 429. Error: {e}. Stopping...")
        return False
