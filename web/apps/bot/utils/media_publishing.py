from ..bot import bot
from .media_processing import create_media_list
from .media_processing import save_media_to_db
from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from decouple import config
from django.db.models import QuerySet
from loguru import logger
from telegram import InputMediaPhoto
from telegram import InputMediaVideo
from telegram import Message


def publish_announcement_media(announcement: Announcement) -> None:
    """
    Публикует медиа данного объявления в канале.

    Эта функция проверяет, сколько медиа-файлов существует для данного объявления,
    и затем публикует их в канале, используя соответствующий метод в зависимости от количества медиа-файлов.

    Args:
        announcement (Announcement): Объявление, медиа которого необходимо опубликовать.
    """

    logger.debug("Starting media publishing process...")

    media: QuerySet[Media] = announcement.media.all()
    logger.debug(f"Media to publish: {media.count()}")

    if not media:
        logger.debug("No media to publish")
        return

    if media.count() < 10:
        _send_less_than_ten_media(announcement, media)
    else:
        _send_more_than_ten_media(announcement, media)


def _send_less_than_ten_media(announcement: Announcement, media: QuerySet[Media]) -> None:
    """
    Отправляет в Telegram набор медиа-файлов, если их меньше 10.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media (QuerySet[Media]): Набор медиа-файлов для публикации.
    """
    media_to_send = create_media_list(media)
    _send_media(announcement, media_to_send)


def _send_more_than_ten_media(announcement: Announcement, media: QuerySet[Media]) -> None:
    """
    Отправляет в Telegram набор медиа-файлов, если их 10 и более, группами по 10.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media (QuerySet[Media]): Набор медиа-файлов для публикации.
    """
    for photo_index in range(0, media.count(), 10):
        media_to_send = create_media_list(media[photo_index : photo_index + 10])
        _send_media(announcement, media_to_send)


def _send_media(
    announcement: Announcement, media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaVideo]]
) -> None:
    """
    Отправляет медиа-файлы и сохраняет информацию о них в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaVideo]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    media_message: list[Message] = perform_action_with_retries(
        bot.send_media_group, chat_id=config("CHANNEL_ID"), media=[x[1] for x in media_to_send]
    )
    if media_message:
        save_media_to_db(announcement, media_message, media_to_send)
