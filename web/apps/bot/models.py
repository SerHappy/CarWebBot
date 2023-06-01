from apps.announcement.models import Announcement
from django.db import models


class PublishedMessage(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"
        MEDIA = "MEDIA", "Media"

    announcement = models.ForeignKey(Announcement, related_name="published_messages", on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=20, choices=MessageType.choices, null=False)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self) -> str:
        return f"Published message {self.message_id} for announcement {self.announcement.name}"
