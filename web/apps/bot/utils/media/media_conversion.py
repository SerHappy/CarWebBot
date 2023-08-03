from apps.announcement.models import Media
from telethon.tl.types import InputMediaPhoto
from telethon.tl.types import InputMediaUploadedDocument


def create_media(media_file: Media) -> InputMediaPhoto | InputMediaUploadedDocument:
    """
    Создает медиа-объект для отправки в Telegram.

    Args:
        media_file (Media): Медиа-файл для преобразования.

    Returns:
        InputMediaPhoto | InputMediaUploadedDocument: Медиа-объект для отправки в Telegram.
    """
    return _get_file_path(media_file)


def _get_file_path(media_file: Media) -> str:
    """
    Возвращает путь до файла на сервере.

    Args:
        media_file (Media): Медиа-файл.

    Returns:
        str: Путь до файла.
    """
    return media_file.file.path
