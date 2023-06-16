from ..models import PublishedMessage
from .media_conversion import create_media
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from django.db.models import QuerySet
from loguru import logger
from telebot.types import Message
from telegram import InputMediaPhoto
from telegram import InputMediaVideo


def create_media_list(media: QuerySet[Media]) -> list[tuple[Media, InputMediaPhoto | InputMediaVideo]]:
    """
    Создает список медиа-объектов для отправки в Telegram.

    Args:
        media (QuerySet[Media]): Набор медиа-файлов, которые нужно преобразовать в медиа-объекты.

    Returns:
        list[tuple[Media, InputMediaPhoto]]: Список кортежей, каждый из которых содержит оригинальный медиа-файл
                                              и соответствующий ему медиа-объект для отправки в Telegram.
    """
    logger.debug(f"Creating media list from {media}")
    media_to_send = []
    for media_file in media:
        media_to_send.append((media_file, create_media(media_file)))
    return media_to_send


def _save_media_published_message(
    announcement: Announcement,
    sent_media: Message,
    media_to_send_item: Media,
) -> None:
    """
    Создает запись `PublishedMessage` в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        sent_media: Отправленные медиа-данные.
        media_to_send_item (Media): Элемент медиа-данных, который нужно сохранить.
    """
    logger.debug(f"Saving media from message id {sent_media.message_id}")
    logger.debug(f"sent_media: {sent_media}")
    logger.debug(f"Media to send item: {media_to_send_item}")
    PublishedMessage.objects.create(
        announcement=announcement,
        channel_id=sent_media.chat.id,
        message_id=sent_media.message_id,
        media=media_to_send_item,
        type=PublishedMessage.MessageType.MEDIA,
    )
    logger.debug(f"Media from message id {sent_media.message_id} saved to database")


def save_media_to_db(
    announcement: Announcement,
    media_message: PublishedMessage,
    media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaVideo]],
) -> None:
    """
    Сохраняет медиа-файлы в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_message: Отправленные медиа-данные.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaVideo]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    for index, sent_media in enumerate(media_message):
        _save_media_published_message(announcement, sent_media, media_to_send[index][0])
