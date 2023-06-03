from .models import PublishedMessage
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from decouple import config
from django.db.models import QuerySet
from loguru import logger
from telebot import TeleBot
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo
from typing import Literal
from typing import LiteralString


bot = TeleBot(config("TELEGRAM_BOT_TOKEN"))


def create_media_list(media: QuerySet[Media]) -> list[tuple[Media, InputMediaPhoto]]:
    logger.debug(f"Creating media list from {media}")
    media_to_send = []
    for media_file in media:
        logger.debug(f"Processing file {media_file}")
        with open(media_file.file.path, "rb") as file:
            if media_file.media_type == Media.MediaType.PHOTO:
                logger.debug("Creating photo media")
                file_to_send = InputMediaPhoto(file.read())
            else:
                logger.debug("Creating video media")
                file_to_send = InputMediaVideo(file.read())
            media_to_send.append((media_file, file_to_send))
            logger.debug(f"Media created and added to list: {file_to_send}")
    return media_to_send


def save_media_to_db(announcement: Announcement, media_message, media_to_send) -> None:
    for index, sent_media in enumerate(media_message):
        logger.debug(f"Saving media from message id {sent_media.message_id}")
        PublishedMessage.objects.create(
            announcement=announcement,
            message_id=sent_media.message_id,
            media=media_to_send[index][0],
            type=PublishedMessage.MessageType.MEDIA,
        )
        logger.debug(f"Media from message id {sent_media.message_id} saved to database")


def send_media(announcement: Announcement, media_to_send: list[tuple[Media, InputMediaPhoto]]) -> None:
    logger.info(f"Sending media to channel {config('CHANNEL_ID')}")
    media_message = bot.send_media_group(config("CHANNEL_ID"), [x[1] for x in media_to_send])
    logger.info(f"Media sent {media_message}")
    logger.debug("Saving media to database")
    save_media_to_db(announcement, media_message, media_to_send)
    logger.debug("Media saved to database")


def create_media(media_file: Media) -> InputMediaPhoto | InputMediaVideo:
    logger.debug(f"Processing file {media_file}")
    with open(media_file.file.path, "rb") as file:
        if media_file.media_type == Media.MediaType.PHOTO:
            logger.debug("Creating photo media")
            return InputMediaPhoto(file.read())
        else:
            logger.debug("Creating video media")
            return InputMediaVideo(file.read())


def _publish_announcement_media(announcement: Announcement) -> None:
    """Publish media (if exists) of a given announcement to channel"""

    logger.debug("Starting media publishing process...")

    media: QuerySet[Media] = announcement.media.all()
    logger.debug(f"Media to publish: {media.count()}")

    if not media:
        logger.debug("No media to publish")
        return

    if len(media) < 10:
        logger.debug("Less than 10 media to publish")
        media_to_send = create_media_list(media)
        logger.debug("Media list created")
        send_media(announcement, media_to_send)
        logger.debug("Media sent")
        return

    logger.debug("More than 10 media to publish")
    for photo_index in range(0, len(media), 10):
        logger.debug(f"Publishing media from {photo_index} to {photo_index + 10}")
        media_to_send = create_media_list(media[photo_index : photo_index + 10])
        logger.debug("Media list created")
        send_media(announcement, media_to_send)
        logger.debug("Media sent")


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString | Literal["Тегов нет"]:
    tags = announcement.tags.all()
    if tags:
        return f"Теги: {', '.join([tag.name for tag in tags])}"
    return "Тегов нет"


def _prepare_announcement_text(announcement: Announcement) -> LiteralString | Literal["Текста нет"]:
    if announcement.text:
        return f"Текст: {announcement.text}"
    return "Текста нет"


def create_announcement_message(announcement: Announcement) -> str:
    return (
        "Название:"
        f" {announcement.name}\n{_prepare_announcement_text(announcement)}\n{_prepare_announcement_tags(announcement)}"
    )


def publish_announcement_to_channel(announcement: Announcement) -> None:
    """Publish a given announcement to channel"""
    logger.info(f"Publishing announcement: {announcement.name}")
    message = create_announcement_message(announcement)
    logger.debug("Text message created")
    _publish_announcement_media(announcement)
    logger.debug("Media published")
    text_message = bot.send_message(config("CHANNEL_ID"), message)
    logger.info(f"Announcement {announcement.name} published")
    announcement.is_published = True
    announcement.save()
    logger.debug("Announcement saved to database")
    PublishedMessage.objects.create(
        announcement=announcement,
        message_id=text_message.message_id,
        type=PublishedMessage.MessageType.TEXT,
    )
    logger.debug("Text message saved to database")


def delete_announcement_from_channel(announcement: Announcement) -> None:
    """Delete a given announcement from channel"""
    logger.info(f"Deleting announcement: {announcement.name}")
    published_messages: QuerySet[PublishedMessage] = announcement.published_messages.all()
    logger.debug(f"Deleting {published_messages.count()} messages")
    for message in published_messages:
        bot.delete_message(config("CHANNEL_ID"), message.message_id)
        message.delete()
        logger.debug(f"Message {message.message_id} deleted from channel and database")
    announcement.is_published = False
    announcement.is_active = False
    announcement.save()
    logger.info(f"Announcement {announcement.name} deleted from channel")


def edit_announcement_in_channel(announcement: Announcement) -> None:
    """Edit a given announcement in channel"""
    logger.info(f"Editing announcement: {announcement.name}")
    published_messages: QuerySet[PublishedMessage] = announcement.published_messages.all()
    logger.debug(f"Editing {published_messages.count()} messages")

    media: QuerySet[Media] = announcement.media.all()
    logger.debug(f"Media to edit: {media.count()}")

    for index, message in enumerate(published_messages):
        if message.type == PublishedMessage.MessageType.MEDIA:
            if message.media != None:
                logger.debug(f"Not changing media for message {message.message_id}")
                continue
            try:
                logger.debug(f"Editing media for message {message.message_id}")
                bot.edit_message_media(
                    chat_id=config("CHANNEL_ID"),
                    message_id=message.message_id,
                    media=create_media(media[index]),
                )
                logger.debug(f"Media edited for message {message.message_id}")
                PublishedMessage.objects.filter(message_id=message.message_id).update(media=media[index])
                logger.debug(f"Media saved to database for message {message.message_id}")
            except Exception as e:
                logger.error(f"Error while editing message {message.message_id}: {e}\nSkipping...")
        else:
            try:
                logger.debug(f"Editing text for message {message.message_id}")
                bot.edit_message_text(
                    create_announcement_message(announcement),
                    config("CHANNEL_ID"),
                    message.message_id,
                )
                logger.debug(f"Text edited for message {message.message_id}")
            except Exception as e:
                logger.error(f"Error while editing message {message.message_id}: {e}\nSkipping...")
    logger.info(f"Announcement {announcement.name} edited")
