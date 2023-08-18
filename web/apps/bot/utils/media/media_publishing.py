from ..telegram import perform_action_with_retries
from .media_conversion import create_media
from .media_processing import create_media_list
from .media_processing import save_media_to_db
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.bot.models import SubchannelMessage
from apps.bot.services import telethon
from apps.tag.models import Tag
from django.conf import settings
from django.db.models import QuerySet
from loguru import logger
from telethon.sync import TelegramClient
from telethon.tl.types import InputMediaPhoto
from telethon.tl.types import InputMediaUploadedDocument


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


def publish_subchannel_media(announcement: Announcement, tag: Tag) -> None:
    """
    Публикует первое медиа данного объявления в подканале.

    Args:
        announcement (Announcement): Объявление, медиа которого необходимо опубликовать.
        tag (Tag): Тег, подканал которого следует использовать для публикации.
    """
    logger.debug("Starting media publishing process for subchannel...")

    media: QuerySet[Media] = announcement.media.first()

    if not media:
        logger.debug("No media to publish")
        return

    _send_first_media_to_subchannel(announcement, media, tag)


def _send_first_media_to_subchannel(announcement: Announcement, media: Media, tag: Tag) -> None:
    """
    Отправляет первое медиа объявления в подканал.

    Args:
        announcement (Announcement): Объявление, медиа которого необходимо опубликовать.
        media (Media): Медиа для отправки.
        tag (Tag): Тег, подканал которого следует использовать для публикации.
    """
    media_message = telethon.run_in_new_thread(_send_first_media, media, tag)
    if media_message is not None:
        SubchannelMessage.objects.create(
            announcement=announcement,
            channel_id=tag.channel_id,
            message_id=media_message.id,
            type=SubchannelMessage.MessageType.MEDIA,
            tag=tag,
            media=media,
        )


def _send_first_media(media: Media, tag: Tag) -> None:
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        if media.media_type == Media.MediaType.PHOTO or media.media_type == Media.MediaType.VIDEO:
            media_message = perform_action_with_retries(
                client.send_file,
                entity=int(tag.channel_id),
                file=create_media(media),
            )
        return media_message


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
    announcement: Announcement, media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaUploadedDocument]]
) -> None:
    """
    Отправляет медиа-файлы и сохраняет информацию о них в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaUploadedDocument]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    files_to_send = [x[1] for x in media_to_send]
    logger.debug(f"Sending {files_to_send} media files to Telegram...")
    media_message = telethon.run_in_new_thread(_send_media_to_subchannel, media_to_send=media_to_send)
    logger.debug(f"Media message sent result: {media_message}")
    if media_message:
        logger.debug("Saving media to database...")
        save_media_to_db(announcement, media_message, media_to_send)
        logger.debug("Media saved to database")


def _send_media_to_subchannel(
    media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaUploadedDocument]],
) -> None:
    """
    Отправляет медиа-файлы и сохраняет информацию о них в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaUploadedDocument]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    telethon.set_new_event_loop()
    files_to_send = [x[1] for x in media_to_send]
    logger.debug(f"Sending {files_to_send} media files to Telegram...")
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        media_message = perform_action_with_retries(
            client.send_file,
            entity=settings.MAIN_CHANNEL_ID,
            file=files_to_send,
        )
        logger.debug(f"Media message sent result: {media_message}")
        return media_message
