from ..bot import bot
from .telegram import perform_action_with_retries
from apps.announcement.models import Media
from decouple import config
from django.conf import settings
from loguru import logger
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo
from urllib.parse import urljoin


def create_media(media_file: Media) -> InputMediaPhoto | InputMediaVideo:
    """
    Создает медиа-объект для отправки в Telegram.

    Args:
        media_file (Media): Медиа-файл для преобразования.

    Returns:
        InputMediaPhoto | InputMediaVideo: Медиа-объект для отправки в Telegram.
    """
    logger.debug(f"Creating media from {media_file}")
    file_path = _get_file_path(media_file)
    logger.debug(f"File path: {file_path}")
    if media_file.media_type == Media.MediaType.PHOTO:
        file_id = perform_action_with_retries(_upload_file, file_path, "photo")
        return InputMediaPhoto(file_id)
    elif media_file.media_type == Media.MediaType.VIDEO:
        file_id = perform_action_with_retries(_upload_file, file_path, "video")
        return InputMediaVideo(file_id)
    else:
        raise ValueError(f"Unknown media type {media_file.media_type}")


def _upload_file(file_path: str, media_type: str) -> str:
    """
    Загружает файл в Telegram и возвращает его file_id.

    Args:
        file_path (str): Путь до файла на сервере.
        media_type (str): Тип медиа-файла, "photo" или "video".

    Returns:
        str: file_id в Telegram.
    """
    logger.debug(f"Uploading file {file_path} to Telegram")
    with open(file_path, "rb") as file:
        logger.debug(f"File opened")
        if media_type == "photo":
            response = bot.send_photo(chat_id=config("MEDIA_CHANNEL_ID"), photo=file)
            file_id = response.photo[-1].file_id
        elif media_type == "video":
            response = bot.send_video(chat_id=config("MEDIA_CHANNEL_ID"), video=file)
            file_id = response.video.file_id
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

        bot.delete_message(chat_id=config("MEDIA_CHANNEL_ID"), message_id=response.message_id)

    return file_id


def _get_file_path(media_file: Media) -> str:
    """
    Возвращает путь до файла на сервере.

    Args:
        media_file (Media): Медиа-файл.

    Returns:
        str: Путь до файла.
    """
    return media_file.file.path
