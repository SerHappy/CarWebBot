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
from typing import Any
from typing import Callable
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
    if e.error_code == 400:
        logger.warning(f"Received 400 error from Telegram.")
        return False
    else:
        logger.critical(f"Error is not 429. Error: {e}. Stopping...")
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


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString | Literal["Тегов нет"]:
    """
    Подготавливает строку тегов для данного объявления.

    Args:
        announcement (Announcement): Объявление, теги которого необходимо подготовить.

    Returns:
        LiteralString | Literal["Тегов нет"]: Возвращает строку с перечисленными тегами или строку "Тегов нет",
        если теги отсутствуют.
    """
    tags = announcement.tags.all()
    if tags:
        return f"Теги: {', '.join([tag.name for tag in tags])}"
    return "Тегов нет"


def _prepare_announcement_text(announcement: Announcement) -> LiteralString | Literal["Текста нет"]:
    """
    Подготавливает текст объявления.

    Args:
        announcement (Announcement): Объявление, текст которого необходимо подготовить.

    Returns:
        LiteralString | Literal["Текста нет"]: Возвращает строку с текстом объявления или строку "Текста нет",
        если текст отсутствует.
    """
    if announcement.text:
        return f"Текст: {announcement.text}"
    return "Текста нет"


def _create_announcement_message(announcement: Announcement) -> str:
    """
    Создает текстовое сообщение для данного объявления.

    Args:
        announcement (Announcement): Объявление, для которого необходимо создать текстовое сообщение.

    Returns:
        str: Текстовое сообщение, готовое к отправке.
    """
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
    return _perform_action_with_retries(bot.send_message, config("CHANNEL_ID"), message)


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


def _perform_action_with_retries(action: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
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
    raise RuntimeError("Max attempts reached in _perform_action_with_retries")


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


def _update_announcement_media(message: PublishedMessage, new_media: Media) -> None:
    """
    Обновляет медиа для данного сообщения в канале.

    Args:
        message (PublishedMessage): Сообщение, медиа которого необходимо обновить.
        new_media (Media): Новое медиа, которое будет заменять старое.
    """
    logger.debug(f"Editing media for message {message.message_id}")
    _perform_action_with_retries(
        bot.edit_message_media,
        chat_id=config("CHANNEL_ID"),
        message_id=message.message_id,
        media=_create_media(new_media),
    )
    logger.debug(f"Media edited for message {message.message_id}")
    PublishedMessage.objects.filter(message_id=message.message_id).update(media=new_media)
    logger.debug(f"Media saved to database for message {message.message_id}")


def _delete_announcement_message(message: PublishedMessage) -> None:
    """
    Удаляет данное сообщение из канала.

    Args:
        message (PublishedMessage): Сообщение, которое нужно удалить.
    """
    logger.debug(f"Deleting message {message.message_id}")
    _perform_action_with_retries(
        bot.delete_message,
        chat_id=config("CHANNEL_ID"),
        message_id=message.message_id,
    )
    PublishedMessage.delete(message)
    logger.debug(f"Message {message.message_id} deleted")


def _edit_announcement_media(announcement: Announcement) -> None:
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


def _edit_announcement_text(announcement: Announcement) -> None:
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
        new_text = _create_announcement_message(announcement)
        _perform_action_with_retries(
            bot.edit_message_text,
            chat_id=config("CHANNEL_ID"),
            message_id=text_message.message_id,
            text=new_text,
        )
        logger.debug(f"Text message {text_message.message_id} edited")
    else:
        logger.warning(f"Text message for announcement {announcement.name} not found")

    logger.debug(f"Text edited for announcement: {announcement.name}")


def edit_announcement_in_channel(announcement: Announcement) -> None:
    """
    Редактирует объявление в канале, обновляя все связанные медиа и текстовые сообщения.

    Args:
        announcement (Announcement): Объявление, которое нужно отредактировать.
    """
    logger.info(f"Editing announcement: {announcement.name}")
    _edit_announcement_media(announcement)
    _edit_announcement_text(announcement)
    logger.info(f"Announcement {announcement.name} edited")
