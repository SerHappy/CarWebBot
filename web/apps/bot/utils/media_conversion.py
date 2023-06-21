from apps.announcement.models import Media
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
    file_url = _get_file_url(media_file)
    if media_file.media_type == Media.MediaType.PHOTO:
        return _create_photo_media(file_url)
    elif media_file.media_type == Media.MediaType.VIDEO:
        return _create_video_media(file_url)
    else:
        raise ValueError(f"Unknown media type {media_file.media_type}")


def _get_file_url(media_file: Media) -> str:
    """
    Возвращает URL медиа-файла.

    Args:
        media_file (Media): Медиа-файл.

    Returns:
        str: URL медиа-файла.
    """
    return urljoin(settings.BASE_URL, media_file.file.url)


def _create_photo_media(file_url: str) -> InputMediaPhoto:
    """
    Создает объект фото-медиа для отправки в Telegram.

    Args:
        file_url (str): URL файла.

    Returns:
        InputMediaPhoto: Фото-медиа объект для отправки в Telegram.
    """
    logger.debug(f"Creating photo media from {file_url}")
    return InputMediaPhoto(file_url)


def _create_video_media(file_url: str) -> InputMediaVideo:
    """
    Создает объект видео-медиа для отправки в Telegram.

    Args:
        file_url (str): URL файла.

    Returns:
        InputMediaVideo: Видео-медиа объект для отправки в Telegram.
    """
    logger.debug(f"Creating photo media from {file_url}")
    return InputMediaVideo(file_url)
