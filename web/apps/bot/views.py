from .models import PublishedMessage
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from decouple import config
from django.db.models import QuerySet
from loguru import logger
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import InputMediaPhoto
from telebot.types import InputMediaVideo
from typing import Literal
from typing import LiteralString

import time


# Инициализируем очередь сообщений
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
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            logger.info(f"Sending media to channel {config('CHANNEL_ID')}")
            media_message = bot.send_media_group(config("CHANNEL_ID"), [x[1] for x in media_to_send])
            logger.info(f"Media sent {media_message}")
            logger.debug("Saving media to database")
            save_media_to_db(announcement, media_message, media_to_send)
            logger.debug("Media saved to database")
            break
        except ApiTelegramException as e:
            logger.error(f"Error while sending media: {e}")
            if e.error_code == 429:
                attempt += 1
                retry_after = int(e.description.split(" ")[-1]) + 1
                logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                logger.warning("Waking up and trying again...")
            else:
                logger.critical("Error is not 429. Stopping...")
                break


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
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            logger.debug(f"Sending message to channel {config('CHANNEL_ID')}")
            text_message = bot.send_message(config("CHANNEL_ID"), message)
            logger.debug(f"Message sent {text_message}")
            break
        except ApiTelegramException as e:
            if e.error_code == 429:
                attempt += 1
                retry_after = int(e.description.split(" ")[-1]) + 1
                logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                logger.warning("Waking up and trying again...")
            else:
                logger.critical("Error is not 429. Stopping...")
                break
    logger.info(f"Announcement {announcement.name} published")
    announcement.published_message_link = f"https://t.me/{config('CHANNEL_NAME')}/{text_message.message_id}"
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
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            try:
                bot.delete_message(config("CHANNEL_ID"), message.message_id)
                message.delete()
                logger.debug(f"Message {message.message_id} deleted from channel and database")
                break
            except ApiTelegramException as e:
                if e.error_code == 429:
                    attempt += 1
                    retry_after = int(e.description.split(" ")[-1]) + 1
                    logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
                    time.sleep(retry_after)
                    logger.warning("Waking up and trying again...")
                elif e.error_code == 400:
                    logger.warning(f"Message {message.message_id} already deleted from channel")
                    break
                else:
                    logger.critical("Error is not 429 or 400. Stopping...")
                    break
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

    current_media_count = announcement.media.filter(media_type__in=["PHOTO", "VIDEO"]).count()

    for index, message in enumerate(published_messages):
        if message.type == PublishedMessage.MessageType.MEDIA:
            if index >= current_media_count:
                try:
                    logger.debug(f"Deleting message {message.message_id}")
                    bot.delete_message(chat_id=config("CHANNEL_ID"), message_id=message.message_id)
                    PublishedMessage.delete(message)
                    logger.debug(f"Message {message.message_id} deleted")
                except ApiTelegramException as e:
                    logger.error(f"Failed to delete message {message.message_id}: {e}")
            else:
                if message.media != None:
                    logger.debug(f"Not changing media for message {message.message_id}")
                    continue
                max_attempts = 5
                attempt = 0
                while attempt < max_attempts:
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
                        break
                    except ApiTelegramException as e:
                        if e.error_code == 429:
                            attempt += 1
                            retry_after = int(e.description.split(" ")[-1]) + 1
                            logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
                            time.sleep(retry_after)
                            logger.warning("Waking up and trying again...")
                        elif e.error_code == 400:
                            logger.warning(f"Message {message.message_id} can't be edited. Skipping...")
                            break
                        else:
                            logger.critical("Error is not 429 or 400. Stopping...")
                            break
        else:
            max_attempts = 5
            attempt = 0
            while attempt < max_attempts:
                try:
                    logger.debug(f"Editing text for message {message.message_id}")
                    bot.edit_message_text(
                        create_announcement_message(announcement),
                        config("CHANNEL_ID"),
                        message.message_id,
                    )
                    logger.debug(f"Text edited for message {message.message_id}")
                    break
                except ApiTelegramException as e:
                    if e.error_code == 429:
                        attempt += 1
                        retry_after = int(e.description.split(" ")[-1]) + 1
                        logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
                        time.sleep(retry_after)
                        logger.warning("Waking up and trying again...")
                    elif e.error_code == 400:
                        logger.warning(f"Message {message.message_id} can't be edited. Skipping...")
                        break
                    else:
                        logger.critical("Error is not 429 or 400. Stopping...")
                        break
    logger.info(f"Announcement {announcement.name} edited")
