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


# Инициализируем бота
bot = TeleBot(config("TELEGRAM_BOT_TOKEN"))


def _handle_telegram_exception(e: ApiTelegramException) -> bool:
    """
    Обрабатывает исключения, связанные с Telegram API.

    Args:
        e (ApiTelegramException): Исключение, которое нужно обработать.

    Returns:
        bool: Возвращает True, если исключение обработано и необходимо повторить попытку.
              Возвращает False, если обработка исключения не удалась.
    """
    if e.error_code == 429:
        retry_after = int(e.description.split(" ")[-1]) + 1
        logger.warning(f"Received 429 error from Telegram. Sleeping for {retry_after} seconds...")
        time.sleep(retry_after)
        logger.warning("Waking up and trying again...")
        return True
    else:
        logger.critical("Error is not 429. Stopping...")
        return False


def _read_file(media_file: Media) -> bytes:
    """
    Открывает и читает содержимое файла.

    Args:
        media_file (Media): Медиа-файл для чтения.

    Returns:
        bytes: Содержимое файла.
    """
    with open(media_file.file.path, "rb") as file:
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


def _create_media(media_file: Media) -> InputMediaPhoto | InputMediaVideo:
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


def _create_media(media_file: Media) -> InputMediaPhoto | InputMediaVideo:
    """
    Создает медиа-объект для отправки в Telegram.

    Args:
        media_file (Media): Медиа-файл, который нужно преобразовать в медиа-объект.

    Returns:
        InputMediaPhoto | InputMediaVideo: Медиа-объект для отправки в Telegram.
    """
    logger.debug(f"Processing file {media_file}")
    with open(media_file.file.path, "rb") as file:
        if media_file.media_type == Media.MediaType.PHOTO:
            logger.debug("Creating photo media")
            return InputMediaPhoto(file.read())
        elif media_file.media_type == Media.MediaType.VIDEO:
            logger.debug("Creating video media")
            return InputMediaVideo(file.read())
        else:
            raise ValueError(f"Unknown media type {media_file.media_type}")


def _create_media_list(media: QuerySet[Media]) -> list[tuple[Media, InputMediaPhoto]]:
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
        media_to_send.append((media_file, _create_media(media_file)))
    return media_to_send


def _create_published_message(announcement: Announcement, sent_media, media_to_send_item) -> None:
    """
    Создает запись `PublishedMessage` в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        sent_media: Отправленные медиа-данные.
        media_to_send_item (Media): Элемент медиа-данных, который нужно сохранить.
    """
    logger.debug(f"Saving media from message id {sent_media.message_id}")
    PublishedMessage.objects.create(
        announcement=announcement,
        message_id=sent_media.message_id,
        media=media_to_send_item,
        type=PublishedMessage.MessageType.MEDIA,
    )
    logger.debug(f"Media from message id {sent_media.message_id} saved to database")


def _save_media_to_db(announcement: Announcement, media_message, media_to_send) -> None:
    """
    Сохраняет медиа-файлы в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_message: Отправленные медиа-данные.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaVideo]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    for index, sent_media in enumerate(media_message):
        _create_published_message(announcement, sent_media, media_to_send[index][0])


def _send_media_with_retries(media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaVideo]]) -> None:
    """
    Отправляет медиа в Telegram с несколькими попытками.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaVideo]]):
        Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            media_message = bot.send_media_group(config("CHANNEL_ID"), [x[1] for x in media_to_send])
            return media_message
        except ApiTelegramException as e:
            if _handle_telegram_exception(e):
                attempt += 1
            else:
                break


def send_media(
    announcement: Announcement, media_to_send: list[tuple[Media, InputMediaPhoto | InputMediaVideo]]
) -> None:
    """
    Отправляет медиа-файлы и сохраняет информацию о них в базе данных.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media_to_send (list[tuple[Media, InputMediaPhoto | InputMediaVideo]]): Список кортежей, каждый из которых содержит медиа-файл и соответствующий медиа-объект.
    """
    media_message = _send_media_with_retries(media_to_send)
    if media_message:
        _save_media_to_db(announcement, media_message, media_to_send)


def _send_less_than_ten_media(announcement: Announcement, media: QuerySet[Media]) -> None:
    """
    Отправляет в Telegram набор медиа-файлов, если их меньше 10.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media (QuerySet[Media]): Набор медиа-файлов для публикации.
    """
    media_to_send = _create_media_list(media)
    send_media(announcement, media_to_send)


def _send_more_than_ten_media(announcement: Announcement, media: QuerySet[Media]) -> None:
    """
    Отправляет в Telegram набор медиа-файлов, если их 10 и более, группами по 10.

    Args:
        announcement (Announcement): Объявление, с которым связаны медиа-файлы.
        media (QuerySet[Media]): Набор медиа-файлов для публикации.
    """
    for photo_index in range(0, media.count(), 10):
        media_to_send = _create_media_list(media[photo_index : photo_index + 10])
        send_media(announcement, media_to_send)


def _publish_announcement_media(announcement: Announcement) -> None:
    """Publish media (if exists) of a given announcement to channel"""

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


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString | Literal["Тегов нет"]:
    tags = announcement.tags.all()
    if tags:
        return f"Теги: {', '.join([tag.name for tag in tags])}"
    return "Тегов нет"


def _prepare_announcement_text(announcement: Announcement) -> LiteralString | Literal["Текста нет"]:
    if announcement.text:
        return f"Текст: {announcement.text}"
    return "Текста нет"


def _create_announcement_message(announcement: Announcement) -> str:
    return (
        "Название:"
        f" {announcement.name}\n{_prepare_announcement_text(announcement)}\n{_prepare_announcement_tags(announcement)}"
    )


def _send_text_message_with_retries(message: str) -> str | None:
    """
    Отправляет текстовое сообщение в Telegram с несколькими попытками.

    Args:
        message (str): Текст сообщения для отправки.

    Returns:
        Optional[str]: Возвращает объект сообщения, если сообщение успешно отправлено.
                       Возвращает None, если отправка сообщения не удалась.
    """
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            text_message = bot.send_message(config("CHANNEL_ID"), message)
            return text_message
        except ApiTelegramException as e:
            if not _handle_telegram_exception(e):
                break


def _update_announcement_and_save_message(announcement: Announcement, text_message: str) -> None:
    """
    Обновляет данные объявления и сохраняет информацию о сообщении в базе данных.

    Args:
        announcement (Announcement): Объявление для обновления.
        text_message (str): Объект сообщения, информация о котором будет сохранена в базе данных.
    """
    announcement.published_message_link = f"https://t.me/{config('CHANNEL_NAME')}/{text_message.message_id}"
    announcement.is_published = True
    announcement.save()
    PublishedMessage.objects.create(
        announcement=announcement,
        message_id=text_message.message_id,
        type=PublishedMessage.MessageType.TEXT,
    )


def _perform_action_with_retries(action, *args, **kwargs):
    """
    Выполняет заданное действие с несколькими попытками в случае ошибок.

    Args:
        action (callable): Действие, которое следует выполнить.
        *args: Позиционные аргументы для действия.
        **kwargs: Именованные аргументы для действия.
    """
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            return action(*args, **kwargs)
        except ApiTelegramException as e:
            if not _handle_telegram_exception(e):
                break
        attempt += 1
    return None


def publish_announcement_to_channel(announcement: Announcement) -> None:
    """
    Публикует данное объявление в канале.

    Args:
        announcement (Announcement): Объявление для публикации.
    """
    logger.info(f"Publishing announcement: {announcement.name}")
    message = _create_announcement_message(announcement)
    _publish_announcement_media(announcement)
    text_message = _send_text_message_with_retries(message)
    if text_message:
        logger.info(f"Announcement {announcement.name} published")
        _update_announcement_and_save_message(announcement, text_message)


def _update_announcement_status(announcement: Announcement, is_published: bool, is_active: bool) -> None:
    """
    Обновляет статус объявления в базе данных.

    Args:
        announcement (Announcement): Объявление, статус которого необходимо обновить.
        is_published (bool): Статус публикации объявления.
        is_active (bool): Статус активности объявления.
    """
    announcement.is_published = is_published
    announcement.is_active = is_active
    announcement.save()
    logger.info(f"Announcement {announcement.name} status updated in database")


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
        _perform_action_with_retries(bot.delete_message, config("CHANNEL_ID"), message.message_id)
        message.delete()
        logger.debug(f"Message {message.message_id} deleted from channel and database")
    _update_announcement_status(announcement, is_published=False, is_active=False)
    logger.info(f"Announcement {announcement.name} deleted from channel")


def _edit_media_message(message, message_to_media) -> None:
    """
    Редактирует или удаляет медиа-сообщение.

    Args:
        message (PublishedMessage): Сообщение, которое нужно отредактировать или удалить.
        message_to_media (dict): Словарь связывающий идентификаторы сообщений с медиафайлами.
    """
    media = message_to_media.get(message.id)

    if not media:
        _perform_action_with_retries(bot.delete_message, chat_id=config("CHANNEL_ID"), message_id=message.message_id)
        PublishedMessage.delete(message)
        logger.debug(f"Message {message.message_id} deleted")
    else:
        _perform_action_with_retries(
            bot.edit_message_media,
            chat_id=config("CHANNEL_ID"),
            message_id=message.message_id,
            media=_create_media(media),
        )
        PublishedMessage.objects.filter(message_id=message.message_id).update(media=media)
        logger.debug(f"Media saved to database for message {message.message_id}")


def _edit_text_message(message, announcement):
    """
    Редактирует текстовое сообщение.

    Args:
        message (PublishedMessage): Сообщение, которое нужно отредактировать.
        announcement (Announcement): Объявление, связанное с сообщением.
    """
    _perform_action_with_retries(
        bot.edit_message_text,
        _create_announcement_message(announcement),
        config("CHANNEL_ID"),
        message.message_id,
    )
    logger.debug(f"Text edited for message {message.message_id}")


def edit_announcement_in_channel(announcement: Announcement) -> None:
    """
    Редактирует данное объявление в канале.

    Args:
        announcement (Announcement): Объявление, которое необходимо отредактировать.
    """
    logger.info(f"Editing announcement: {announcement.name}")
    published_messages: QuerySet[PublishedMessage] = announcement.published_messages.all()
    logger.debug(f"Editing {published_messages.count()} messages")

    media: QuerySet[Media] = announcement.media.all()
    logger.debug(f"Media to edit: {media.count()}")

    # Создание словаря для связи идентификатора сообщения и соответствующего медиафайла
    message_to_media = {message.id: media for message, media in zip(published_messages, media)}

    for message in published_messages:
        if message.type == PublishedMessage.MessageType.MEDIA:
            _edit_media_message(message, message_to_media)
        else:
            _edit_text_message(message, announcement)
    logger.info(f"Announcement {announcement.name} edited")
