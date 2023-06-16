from .bot import bot
from .models import PublishedMessage
from .utils.announcement_editing import edit_announcement_media
from .utils.announcement_editing import edit_announcement_text
from .utils.announcement_editing import update_announcement_status
from .utils.announcement_publishing import create_announcement_message
from .utils.announcement_publishing import send_text_message_with_retries
from .utils.announcement_publishing import update_announcement_and_save_message
from .utils.media_publishing import publish_announcement_media
from .utils.telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from decouple import config
from django.db.models import QuerySet
from loguru import logger
from telebot import TeleBot


# bot: TeleBot = TeleBot(config("TELEGRAM_BOT_TOKEN", cast=str))  # type: ignore


def publish_announcement_to_channel(announcement: Announcement) -> None:
    """
    Публикует данное объявление в канале.

    Args:
        announcement (Announcement): Объявление для публикации.
    """
    logger.info(f"Publishing announcement: {announcement.name}")
    message = create_announcement_message(announcement)
    publish_announcement_media(announcement)
    text_message = send_text_message_with_retries(message)
    if text_message:
        logger.info(f"Announcement {announcement.name} published")
        update_announcement_and_save_message(announcement, text_message)


def edit_announcement_in_channel(announcement: Announcement) -> None:
    """
    Редактирует объявление в канале, обновляя все связанные медиа и текстовые сообщения.

    Args:
        announcement (Announcement): Объявление, которое нужно отредактировать.
    """
    logger.info(f"Editing announcement: {announcement.name}")
    edit_announcement_media(announcement)
    edit_announcement_text(announcement)
    logger.info(f"Announcement {announcement.name} edited")


def delete_announcement_from_channel(announcement: Announcement) -> None:
    """
    Удаляет данное объявление из канала.

    Args:
        announcement (Announcement): Объявление, которое необходимо удалить.
    """
    logger.info(f"Deleting announcement: {announcement.name}")
    published_messages: QuerySet[PublishedMessage] = announcement.published_messages.all()
    logger.debug(f"Deleting {published_messages.count()} messages")
    for message in published_messages:
        perform_action_with_retries(bot.delete_message, message.channel_id, message.message_id)
        message.delete()
        logger.debug(f"Message {message.message_id} deleted from channel and database")
    update_announcement_status(announcement, is_published=False, is_active=False)
    logger.info(f"Announcement {announcement.name} deleted from channel")
