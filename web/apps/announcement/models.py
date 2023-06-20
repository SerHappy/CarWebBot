from django.db import models
from django.utils.deconstruct import deconstructible

import os
import uuid


class Tag(models.Model):
    name: str = models.CharField(max_length=50, unique=True)
    is_active: bool = models.BooleanField(default=True)
    modified_at: str = models.DateTimeField(auto_now=True)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Tag {self.name}"


class Announcement(models.Model):
    class ProcessingStatus(models.TextChoices):
        PENDING = "P", "Pending"
        PROCESSING = "R", "Processing"
        DONE = "D", "Done"

    name: str = models.CharField(max_length=255, null=False)
    text: str = models.TextField(null=True)
    price: str = models.CharField(max_length=255, null=True)
    tags = models.ManyToManyField(Tag, related_name="announcements")
    status: str = models.CharField(max_length=50, null=True)
    media: "Media"
    note: str = models.TextField(null=True)
    is_published: bool = models.BooleanField(default=False)
    is_active: bool = models.BooleanField(default=True)
    processing_status = models.CharField(
        max_length=1,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    published_message_link: str = models.CharField(max_length=255, null=True)
    publication_date: str = models.DateTimeField(auto_now_add=False, null=True)
    modified_count: int = models.IntegerField(default=0)
    modified_at: str = models.DateTimeField(auto_now=True)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        return f"Announcement {self.name}. Published: {self.is_published}. Date: {self.publication_date}"


@deconstructible
class UniquePathAndRename(object):
    def __call__(self, instance: "Media", filename: str) -> str:
        ext = filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        subdir = str(instance.announcement.id)
        return os.path.join(subdir, filename)


content_file_name = UniquePathAndRename()


class Media(models.Model):
    class MediaType(models.TextChoices):
        PHOTO = "PHOTO", "Photo"
        VIDEO = "VIDEO", "Video"

    media_type: str = models.CharField(max_length=20, choices=MediaType.choices, null=False)
    file: str = models.FileField(upload_to=content_file_name)
    announcement: "Announcement" = models.ForeignKey(
        Announcement, related_name="media", null=False, on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Media {self.file} for announcement {self.announcement.name}"
