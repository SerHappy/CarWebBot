from apps.announcement.models import Media
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo


def create_media(media_file: Media) -> InputMediaPhoto | InputMediaVideo:
    """
    Создает медиа-объект для отправки в Telegram.

    Args:
        media_file (Media): Медиа-файл для преобразования.

    Returns:
        InputMediaPhoto | InputMediaVideo: Медиа-объект для отправки в Telegram.
    """
    file_content = _read_file(media_file)
    if media_file.media_type == Media.MediaType.PHOTO:
        return _create_photo_media(file_content)
    elif media_file.media_type == Media.MediaType.VIDEO:
        return _create_video_media(file_content)
    else:
        raise ValueError(f"Unknown media type {media_file.media_type}")


def _read_file(media_file: Media) -> bytes:
    """
    Открывает и читает содержимое файла.

    Args:
        media_file (Media): Медиа-файл для чтения.

    Returns:
        bytes: Содержимое файла.
    """
    with open(media_file.file.path, "rb") as file:  # type: ignore
        return file.read()


def _create_photo_media(file_content: bytes) -> InputMediaPhoto:
    """
    Создает объект фото-медиа для отправки в Telegram.

    Args:
        file_content (bytes): Содержимое файла.

    Returns:
        InputMediaPhoto: Фото-медиа объект для отправки в Telegram.
    """
    return InputMediaPhoto(file_content)


def _create_video_media(file_content: bytes) -> InputMediaVideo:
    """
    Создает объект видео-медиа для отправки в Telegram.

    Args:
        file_content (bytes): Содержимое файла.

    Returns:
        InputMediaVideo: Видео-медиа объект для отправки в Telegram.
    """
    return InputMediaVideo(file_content)
