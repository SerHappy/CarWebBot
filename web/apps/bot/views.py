from .models import PublishedMessage
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from decouple import config
from loguru import logger
from telebot import TeleBot
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo
from typing import Literal
from typing import LiteralString


bot = TeleBot(config("TELEGRAM_BOT_TOKEN"))


def create_media_list(media: list[Media]) -> list[InputMediaPhoto]:
    media_to_send = []
    for media_file in media:
        logger.debug(f"Processing file {media_file}")
        with open(media_file.file.path, "rb") as file:
            if media_file.media_type == Media.MediaType.PHOTO:
                file_to_send = InputMediaPhoto(file.read())
            else:
                file_to_send = InputMediaVideo(file.read())
            media_to_send.append(file_to_send)
    return media_to_send


def send_media(announcement: Announcement, media_to_send: list[InputMediaPhoto]) -> None:
    media_message = bot.send_media_group(config("CHANNEL_NAME"), media_to_send)
    logger.debug(f"Media sent {media_message}")
    for sent_media in media_message:
        PublishedMessage.objects.create(
            announcement=announcement,
            message_id=sent_media.message_id,
            type=PublishedMessage.MessageType.MEDIA,
        )
    logger.debug("Media saved to database")


def _publish_announcement_media(announcement: Announcement) -> None:
    """Publish media (if exists) of a given announcement to channel"""

    logger.debug("Starting media publishing process...")

    media: list[Media] = announcement.media.all()

    if not media:
        logger.debug("No media to publish")
        return

    if len(media) < 10:
        logger.debug("Less than 10 media to publish")
        media_to_send = create_media_list(media)
        send_media(announcement, media_to_send)
        return

    logger.debug("More than 10 media to publish")
    for photo_index in range(0, len(media), 10):
        logger.debug(f"Publishing media from {photo_index} to {photo_index + 10}")
        send_media(announcement, media[photo_index : photo_index + 10])


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString | Literal["Тегов нет"]:
    tags = announcement.tags.all()
    if tags:
        return f"Теги: {', '.join([tag.name for tag in tags])}"
    return "Тегов нет"


def create_announcement_message(announcement: Announcement) -> str:
    return f"Название: {announcement.name}\nТекст:{announcement.text}\n{_prepare_announcement_tags(announcement)}"


def publish_announcement_to_channel(announcement: Announcement) -> None:
    """Publish a given announcement to channel"""
    logger.info(f"Publishing announcement: {announcement.name}")
    message = create_announcement_message(announcement)
    logger.debug("Message created")
    _publish_announcement_media(announcement)
    logger.debug("Media published")
    text_message = bot.send_message(config("CHANNEL_NAME"), message)
    logger.info(f"Announcement {announcement.name} published")
    announcement.is_published = True
    announcement.save()
    logger.debug("Announcement saved to database")
    PublishedMessage.objects.create(
        announcement=announcement,
        message_id=text_message.message_id,
        type=PublishedMessage.MessageType.TEXT,
    )
    logger.debug("Message saved to database")


def delete_announcement_from_channel(announcement: Announcement) -> None:
    """Delete a given announcement from channel"""
    logger.info(f"Deleting announcement: {announcement.name}")
    published_messages: list[PublishedMessage] = announcement.published_messages.all()
    for message in published_messages:
        bot.delete_message(config("CHANNEL_NAME"), message.message_id)
        message.delete()
    announcement.is_published = False
    announcement.is_active = False
    announcement.save()
    logger.info(f"Announcement {announcement.name} deleted")
