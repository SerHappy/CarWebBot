from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.tag.models import Tag
from django.db import models


# TODO: Rename model name to `ChannelMessage`
class PublishedMessage(models.Model):
    """Класс для модели опубликованного сообщения."""

    class MessageType(models.TextChoices):
        """Класс для типов сообщений."""

        TEXT = "TEXT", "Text"
        MEDIA = "MEDIA", "Media"

    announcement = models.ForeignKey(Announcement, related_name="published_messages", on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255, null=False)
    channel_id = models.CharField(max_length=255, null=False)
    # TODO: Fix A003 error by renaming built-in `type` field to something else
    type = models.CharField(max_length=20, choices=MessageType.choices, null=False)  # noqa: A003
    media = models.ForeignKey(Media, related_name="published_messages", on_delete=models.SET_NULL, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        """Мета-класс для модели опубликованного сообщения."""

        verbose_name = "Опубликованное сообщение"
        verbose_name_plural = "Опубликованные сообщения"

    def __str__(self) -> str:
        """Строковое представление опубликованного сообщения."""
        return f"Published message {self.message_id} for announcement {self.announcement.name}"


class SubchannelMessage(models.Model):
    """Класс для модели сообщения подканала."""

    class MessageType(models.TextChoices):
        """Класс для типов сообщений."""

        TEXT = "TEXT", "Text"
        MEDIA = "MEDIA", "Media"

    announcement = models.ForeignKey(Announcement, related_name="subchannel_messages", on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255, null=False)
    channel_id = models.CharField(max_length=255, null=False)
    # TODO: Fix A003 error by renaming built-in `type` field to something else
    type = models.CharField(max_length=20, choices=MessageType.choices, null=False)  # noqa: A003
    media = models.ForeignKey(Media, related_name="subchannel_messages", on_delete=models.SET_NULL, null=True)
    tag = models.ForeignKey(Tag, related_name="subchannel_messages", on_delete=models.CASCADE, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        """Мета-класс для модели сообщения подканала."""

        verbose_name = "Сообщение подканала"
        verbose_name_plural = "Сообщения подканала"

    def __str__(self) -> str:
        """Строковое представление сообщения подканала."""
        return (
            f"Subchannel message {self.message_id} for announcement {self.announcement.name} with tag {self.tag.name}"
        )
