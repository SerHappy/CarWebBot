from .models import PublishedMessage
from .services import telethon
from .utils.announcement_editing import edit_announcement_media
from .utils.announcement_editing import edit_announcement_text
from .utils.announcement_editing import update_announcement_status
from .utils.announcement_publishing import create_announcement_message
from .utils.announcement_publishing import send_text_message_with_retries
from .utils.announcement_publishing import update_announcement_and_save_message
from .utils.media.media_publishing import publish_announcement_media
from .utils.media.media_publishing import publish_subchannel_media
from .utils.subchannel_editing import edit_announcement_in_subchannels
from .utils.subchannel_publishing import create_subchannel_message
from .utils.subchannel_publishing import send_text_message_with_retries_to_subchannel
from .utils.subchannel_publishing import update_announcement_and_save_subchannel_message
from .utils.telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.bot.models import SubchannelMessage
from apps.tag.models import Tag
from django.db.models import Q
from django.db.models import QuerySet
from loguru import logger
from telethon.sync import TelegramClient


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

        for tag in announcement.tags.filter(Q(channel_id__isnull=False) & ~Q(channel_id__exact="")):
            message = create_subchannel_message(announcement)
            publish_subchannel_media(announcement, tag)
            text_message = send_text_message_with_retries_to_subchannel(message, tag)
            update_announcement_and_save_subchannel_message(announcement, text_message, tag)


# TODO: Переработать полностью, добавить бизнес-логику ко всему приложению
def edit_announcement_in_channel(announcement: Announcement, old_tags: dict[Tag, str]) -> None:
    """
    Редактирует объявление в канале и подканалах, обновляя все связанные медиа и текстовые сообщения.

    Args:
        announcement (Announcement): Объявление, которое нужно отредактировать.
        old_tags (Dict[Tag, str]): Словарь тегов, которые были связаны с объявлением до его редактирования,
            где ключом является тег, а значением - старый channel_id тега.
    """
    logger.info(f"Editing announcement: {announcement.name}")
    edit_announcement_media(announcement)
    edit_announcement_text(announcement)
    edit_announcement_in_subchannels(announcement)

    current_tags = {tag: tag.channel_id for tag in announcement.tags.all()}

    for tag, old_channel_id in old_tags.items():
        if isinstance(tag, str):
            continue
        if tag in current_tags:
            current_channel_id = current_tags.get(tag)
            if old_channel_id and old_channel_id != current_channel_id:
                delete_announcement_from_subchannel(announcement, tag.id)
        else:
            delete_announcement_from_subchannel(announcement, tag.id)

    for tag, channel_id in current_tags.items():
        try:
            if isinstance(list(old_tags.keys())[0], str):
                continue
        except Exception as e:
            logger.error(e)
            pass
        old_channel_id = old_tags.get(tag)
        if old_channel_id != channel_id and channel_id or (tag not in old_tags and channel_id):
            message = create_subchannel_message(announcement)
            publish_subchannel_media(announcement, tag)
            text_message = send_text_message_with_retries_to_subchannel(message, tag)
            if text_message:
                update_announcement_and_save_subchannel_message(announcement, text_message, tag)

    logger.info(f"Announcement {announcement.name} edited")


def delete_announcement_from_channel(announcement: Announcement) -> None:
    logger.info(f"Deleting announcement: {announcement.name}")

    telethon.run_in_new_thread(_delete_messages, announcement)

    update_announcement_status(announcement, Announcement.ProcessingStatus.UNPUBLISHED)
    logger.info(f"Announcement {announcement.name} deleted from channel")


def _delete_messages(announcement: Announcement) -> None:
    telethon.set_new_event_loop()
    with telethon.fetch_telegram_client() as client:
        client: TelegramClient
        published_messages: QuerySet[PublishedMessage] = announcement.published_messages.all()
        logger.debug(f"Deleting {published_messages.count()} messages")
        for message in published_messages:
            perform_action_with_retries(
                client.delete_messages,
                entity=int(message.channel_id),
                message_ids=[int(message.message_id)],
            )
            message.delete()
            logger.debug(f"Message {message.message_id} deleted from channel and database")

        subchannel_messages: QuerySet[SubchannelMessage] = announcement.subchannel_messages.all()
        logger.debug(f"Deleting {subchannel_messages.count()} subchannel messages")
        for message in subchannel_messages:
            perform_action_with_retries(
                client.delete_messages,
                entity=int(message.channel_id),
                message_ids=[int(message.message_id)],
            )
            message.delete()
            logger.debug(f"Subchannel Message {message.message_id} deleted from channel and database")


def delete_announcement_from_subchannel(announcement: Announcement, tag: Tag) -> None:
    """
    Удаляет данное объявление из подканала.

    Args:
        announcement (Announcement): Объявление, которое необходимо удалить.
        tag (Tag): Тег, подканал которого следует использовать для удаления.
    """
    subchannel_messages: QuerySet[SubchannelMessage] = SubchannelMessage.objects.filter(
        announcement=announcement, tag=tag
    )

    telethon.run_in_new_thread(_delete_subchannels_messages, subchannel_messages)


def _delete_subchannels_messages(subchannel_messages: QuerySet[SubchannelMessage]) -> None:
    telethon.set_new_event_loop()
    for message in subchannel_messages:
        with telethon.fetch_telegram_client() as client:
            client: TelegramClient  # type: ignore[no-redef]
            perform_action_with_retries(
                client.delete_messages,
                entity=int(message.channel_id),
                message_ids=[int(message.message_id)],
            )
        message.delete()
