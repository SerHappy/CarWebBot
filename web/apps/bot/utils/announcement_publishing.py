from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.bot.models import PublishedMessage
from apps.bot.services import telethon
from django.conf import settings
from loguru import logger
from telethon.sync import TelegramClient
from telethon.tl.types import Message
from typing import LiteralString


def create_announcement_message(announcement: Announcement) -> str:
    """
    Создает текстовое сообщение для данного объявления.

    Args:
        announcement (Announcement): Объявление, для которого необходимо создать текстовое сообщение.

    Returns:
        str: Текстовое сообщение, готовое к отправке.
    """
    return (
        f"{_prepare_announcement_tags(announcement)}{announcement.name}\n{_prepare_announcement_text(announcement)}🤖"
    )


def send_text_message_with_retries(message: str) -> str | None:
    """
    Отправляет текстовое сообщение в Telegram с несколькими попытками.

    Args:
        message (str): Текст сообщения для отправки.

    Returns:
        Optional[str]: Возвращает объект сообщения, если сообщение успешно отправлено.
                       Возвращает None, если отправка сообщения не удалась.
    """
    logger.info(f"Sending message to channel {settings.MAIN_CHANNEL_NAME}...")
    return telethon.run_in_new_thread(_send_text_message, message)


def _send_text_message(message: str) -> str | None:
    """
    Отправляет текстовое сообщение в Telegram.

    Args:
        message (str): Текст сообщения для отправки.

    Returns:
        Optional[str]: Возвращает объект сообщения, если сообщение успешно отправлено.
                       Возвращает None, если отправка сообщения не удалась.
    """
    logger.info(f"Sending message to channel {settings.MAIN_CHANNEL_NAME}...")
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        return perform_action_with_retries(
            client.send_message,
            entity=settings.MAIN_CHANNEL_ID,
            message=message,
        )


def update_announcement_and_save_message(announcement: Announcement, text_message: Message) -> None:
    """
    Обновляет данные объявления и сохраняет информацию о сообщении в базе данных.

    Args:
        announcement (Announcement): Объявление для обновления.
        text_message (str): Объект сообщения, информация о котором будет сохранена в базе данных.
    """
    logger.info(f"Updating announcement {announcement.id}...")
    announcement.published_message_link = f"https://t.me/{settings.MAIN_CHANNEL_NAME}/{text_message.id}"
    announcement.save()
    PublishedMessage.objects.create(
        announcement=announcement,
        channel_id=settings.MAIN_CHANNEL_ID,
        message_id=int(text_message.id),
        type=PublishedMessage.MessageType.TEXT,
    )


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString:
    """
    Подготавливает строку тегов для данного объявления.

    Args:
        announcement (Announcement): Объявление, теги которого необходимо подготовить.

    Returns:
        LiteralString | Literal[""]: Возвращает строку с перечисленными тегами или пустую строку,
        если теги отсутствуют.
    """
    tags = announcement.tags.filter(type="visible")
    if tags:
        return f"{' '.join([tag.name for tag in tags])}\n"
    return ""


def _prepare_announcement_text(announcement: Announcement) -> LiteralString:
    """
    Подготавливает текст объявления.

    Args:
        announcement (Announcement): Объявление, текст которого необходимо подготовить.

    Returns:
        LiteralString | Literal[""]: Возвращает строку с текстом объявления или пустую строку,
        если текст отсутствует.
    """
    if announcement.text:
        return f"{announcement.text}\n"
    return ""
