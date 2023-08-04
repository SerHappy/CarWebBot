from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.tag.models import Tag
from django.conf import settings
from django.db import models


class PublishedMessage(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"
        MEDIA = "MEDIA", "Media"

    announcement = models.ForeignKey(Announcement, related_name="published_messages", on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255, null=False)
    channel_id = models.CharField(max_length=255, null=False, default=settings.MAIN_CHANNEL_ID)
    type = models.CharField(max_length=20, choices=MessageType.choices, null=False)
    media = models.ForeignKey(Media, related_name="published_messages", on_delete=models.SET_NULL, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self) -> str:
        return f"Published message {self.message_id} for announcement {self.announcement.name}"


class SubchannelMessage(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"
        MEDIA = "MEDIA", "Media"

    announcement = models.ForeignKey(Announcement, related_name="subchannel_messages", on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255, null=False)
    channel_id = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=20, choices=MessageType.choices, null=False)
    media = models.ForeignKey(Media, related_name="subchannel_messages", on_delete=models.SET_NULL, null=True)
    tag = models.ForeignKey(Tag, related_name="subchannel_messages", on_delete=models.CASCADE, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self) -> str:
        return (
            f"Subchannel message {self.message_id} for announcement {self.announcement.name} with tag {self.tag.name}"
        )
