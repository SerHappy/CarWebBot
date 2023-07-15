from ..bot import bot
from .media.media_conversion import create_media
from .subchannel_publishing import create_subchannel_message
from .telegram import perform_action_with_retries
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.bot.models import SubchannelMessage
from apps.tag.models import Tag
from django.db.models import QuerySet
from loguru import logger


def edit_announcement_in_subchannels(announcement: Announcement) -> None:
    """
    Редактирует объявление во всех подканалах, обновляя связанные медиа и текстовые сообщения.

    Args:
        announcement (Announcement): Объявление, которое нужно отредактировать.
    """
    for tag in announcement.tags.all():
        edit_announcement_in_subchannel(announcement, tag)


def edit_announcement_in_subchannel(announcement: Announcement, tag: Tag) -> None:
    """
    Редактирует текст и медиа объявления в подканале.

    Args:
        announcement (Announcement): Объявление, текст и медиа которого нужно отредактировать.
        tag (Tag): Тег, подканал которого следует использовать для редактирования.
    """
    subchannel_text_message = SubchannelMessage.objects.filter(
        announcement=announcement,
        type=SubchannelMessage.MessageType.TEXT,
        tag=tag,
    ).first()

    if subchannel_text_message:
        new_text = create_subchannel_message(announcement)
        perform_action_with_retries(
            bot.edit_message_text,
            chat_id=subchannel_text_message.channel_id,
            message_id=subchannel_text_message.message_id,
            text=new_text,
        )

    subchannel_media_message = SubchannelMessage.objects.filter(
        announcement=announcement,
        type=SubchannelMessage.MessageType.MEDIA,
        tag=tag,
    ).first()

    if subchannel_media_message:
        edit_subchannel_media(announcement, tag)


def edit_subchannel_media(announcement: Announcement, tag: Tag) -> None:
    """
    Редактирует медиа данного объявления в подканале.

    Args:
        announcement (Announcement): Объявление, медиа которого необходимо отредактировать.
        tag (Tag): Тег, подканал которого следует использовать для редактирования.
    """
    logger.debug("Starting media editing process for subchannel...")

    subchannel_media_message = SubchannelMessage.objects.filter(
        announcement=announcement,
        type=SubchannelMessage.MessageType.MEDIA,
        tag=tag,
    ).first()

    if subchannel_media_message:
        media: QuerySet[Media] = announcement.media.first()

        if not media:
            logger.debug("No media to edit")
            return

        _edit_first_media_in_subchannel(media, subchannel_media_message)


def _edit_first_media_in_subchannel(media: Media, subchannel_media_message: SubchannelMessage) -> None:
    """
    Редактирует первое медиа объявления в подканале.

    Args:
        media (Media): Медиа для редактирования.
        subchannel_media_message (SubchannelMessage): Сообщение в подканале, которое необходимо отредактировать.
    """
    perform_action_with_retries(
        bot.edit_message_media,
        chat_id=subchannel_media_message.channel_id,
        message_id=subchannel_media_message.message_id,
        media=create_media(media),
    )
