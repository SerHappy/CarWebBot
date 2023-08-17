from .announcement_publishing import create_announcement_message
from .media.media_processing import create_media
from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.bot.models import PublishedMessage
from apps.bot.services import telethon
from django.db.models import QuerySet
from loguru import logger
from telethon.sync import TelegramClient


def update_announcement_status(announcement: Announcement, status: Announcement.ProcessingStatus) -> None:
    """
    Обновляет статус объявления в базе данных.

    Args:
        announcement (Announcement): Объявление, статус которого необходимо обновить.
        is_published (bool): Статус публикации объявления.
        is_active (bool): Статус активности объявления.
    """
    announcement.processing_status = status
    announcement.save()
    logger.info(f"Announcement {announcement.name} status updated in database")


def edit_announcement_text(announcement: Announcement) -> None:
    """
    Редактирует текстовое сообщение для данного объявления в канале.

    Args:
        announcement (Announcement): Объявление, текстовое сообщение которого нужно отредактировать.
    """
    logger.debug(f"Editing text for announcement: {announcement.name}")

    text_message = PublishedMessage.objects.get(
        announcement=announcement,
        type=PublishedMessage.MessageType.TEXT,
    )
    if text_message:
        new_text = create_announcement_message(announcement)
        telethon.run_in_new_thread(_edit_message, text_message, new_text)

        logger.debug(f"Text message {text_message.message_id} edited")
    else:
        logger.warning(f"Text message for announcement {announcement.name} not found")

    logger.debug(f"Text edited for announcement: {announcement.name}")


def _edit_message(message: PublishedMessage, new_text: str) -> None:
    """
    Редактирует сообщение в канале.

    Args:
        message (PublishedMessage): Сообщение, которое нужно отредактировать.
        new_text (str): Новый текст сообщения.
    """
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        perform_action_with_retries(
            client.edit_message,
            entity=int(message.channel_id),
            message=int(message.message_id),
            text=new_text,
        )
    logger.debug(f"Message {message.message_id} edited")


def edit_announcement_media(announcement: Announcement) -> None:
    """
    Редактирует все медиа-сообщения для данного объявления в канале.

    Args:
        announcement (Announcement): Объявление, медиа сообщения которого нужно отредактировать.
    """
    media: QuerySet[Media] = announcement.media.all()
    logger.debug(f"Media to edit: {media.count()}")
    published_messages: QuerySet[PublishedMessage] = announcement.published_messages.filter(
        type=PublishedMessage.MessageType.MEDIA
    )

    logger.debug(f"Editing media for announcement: {announcement.name}")

    for index, message in enumerate(published_messages):
        if index < media.count():
            new_media = media[index]
            if message.media != new_media:
                _update_announcement_media(message, new_media)
            else:
                logger.debug(f"Media for message {message.message_id} is up to date")
        else:
            _delete_announcement_message(message)

    logger.debug(f"Media edited for announcement: {announcement.name}")


def _delete_announcement_message(message: PublishedMessage) -> None:
    """
    Удаляет данное сообщение из канала.

    Args:
        message (PublishedMessage): Сообщение, которое нужно удалить.
    """
    logger.debug(f"Deleting message {message.message_id}")
    telethon.run_in_new_thread(_delete_message, message)
    PublishedMessage.delete(message)
    logger.debug(f"Message {message.message_id} deleted")


def _delete_message(message_to_delete: PublishedMessage) -> None:
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        perform_action_with_retries(
            client.delete_messages,
            entity=int(message_to_delete.channel_id),
            message_ids=[int(message_to_delete.message_id)],
        )


def _update_announcement_media(message: PublishedMessage, new_media: Media) -> None:
    """
    Обновляет медиа для данного сообщения в канале.

    Args:
        message (PublishedMessage): Сообщение, медиа которого необходимо обновить.
        new_media (Media): Новое медиа, которое будет заменять старое.
    """
    logger.debug(f"Editing media for message {message.message_id}")
    telethon.run_in_new_thread(_edit_media, message, new_media)
    logger.debug(f"Media edited for message {message.message_id}")
    PublishedMessage.objects.filter(message_id=message.message_id).update(media=new_media)
    logger.debug(f"Media saved to database for message {message.message_id}")


def _edit_media(message_to_edit: PublishedMessage, new_media: Media) -> None:
    """Меняет старое медиа на новое `new_media` в сообщении `message_to_edit` в канале."""
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        perform_action_with_retries(
            client.edit_message,
            entity=int(message_to_edit.channel_id),
            message=int(message_to_edit.message_id),
            file=create_media(new_media),
        )
