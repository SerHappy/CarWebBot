from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.bot.models import SubchannelMessage
from apps.bot.services import telethon
from apps.tag.models import Tag
from telethon.sync import TelegramClient
from telethon.tl.types import Message
from typing import LiteralString


def create_subchannel_message(announcement: Announcement) -> str:
    """
    Создает текстовое сообщение для данного объявления для подканала.

    Args:
        announcement (Announcement): Объявление, для которого необходимо создать текстовое сообщение.

    Returns:
        str: Текстовое сообщение, готовое к отправке.
    """
    return (
        f"{_prepare_subchannel_tags(announcement)}{announcement.name}\n{_prepare_subchannel_text(announcement)}🤖"
        f"\n{announcement.published_message_link}"
    )


def send_text_message_with_retries_to_subchannel(message: str, tag: Tag) -> Message | None:
    """
    Отправляет текстовое сообщение в Telegram подканал с несколькими попытками.

    Args:
        message (str): Текст сообщения для отправки.
        tag (Tag): Тег, подканал которого следует использовать для отправки.

    Returns:
        Optional[Message]: Возвращает объект сообщения, если сообщение успешно отправлено.
                       Возвращает None, если отправка сообщения не удалась.
    """
    return telethon.run_in_new_thread(
        _send_message_to_subchannel,
        message=message,
        tag=tag,
    )


def _send_message_to_subchannel(message: str, tag: Tag) -> Message | None:
    """Отправляет текстовое сообщение в Telegram подканал."""
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient  # type: ignore[no-redef]
        return perform_action_with_retries(
            client.send_message,
            entity=int(tag.channel_id),
            message=message,
        )


def update_announcement_and_save_subchannel_message(
    announcement: Announcement, text_message: Message, tag: Tag
) -> None:
    """
    Обновляет данные объявления и сохраняет информацию о сообщении в базе данных для подканала.

    Args:
        announcement (Announcement): Объявление для обновления.
        text_message (str): Объект сообщения, информация о котором будет сохранена в базе данных.
        tag (Tag): Тег, подканал которого следует использовать для сохранения информации.
    """
    SubchannelMessage.objects.create(
        announcement=announcement,
        channel_id=int(tag.channel_id),
        message_id=int(text_message.id),
        type=SubchannelMessage.MessageType.TEXT,
        tag=tag,
    )


def _prepare_subchannel_tags(announcement: Announcement) -> LiteralString:
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


def _prepare_subchannel_text(announcement: Announcement) -> LiteralString:
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
