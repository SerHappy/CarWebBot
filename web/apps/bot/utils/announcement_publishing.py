from ..bot import bot
from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.bot.models import PublishedMessage
from decouple import config
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
    return perform_action_with_retries(bot.send_message, config("CHANNEL_ID"), message)


def update_announcement_and_save_message(announcement: Announcement, text_message: str) -> None:
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
        channel_id=config("CHANNEL_ID"),
        message_id=text_message.message_id,
        type=PublishedMessage.MessageType.TEXT,
    )


def _prepare_announcement_tags(announcement: Announcement) -> LiteralString:
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
        return f"{', '.join([tag.name for tag in tags])}\n"
    return ""


def _prepare_announcement_text(announcement: Announcement) -> LiteralString:
    """
    Подготавливает текст объявления.

    Args:
        announcement (Announcement): Объявление, текст которого необходимо подготовить.

    Returns:
        LiteralString | Literal["Текста нет"]: Возвращает строку с текстом объявления или строку "Текста нет",
        если текст отсутствует.
    """
    if announcement.text:
        return f"{announcement.text}\n"
    return ""
