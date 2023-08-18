from ..tag.models import Tag
from django.db import models
from django.utils.deconstruct import deconstructible

import os
import uuid


class Announcement(models.Model):
    """Модель объявления."""

    class ProcessingStatus(models.TextChoices):
        """Статусы обработки объявления."""

        AWAITING_PUBLICATION = "AWAITING", "Awaiting Publication"
        PUBLISHED = "PUBLISHED", "Published"
        UNPUBLISHED = "UNPUBLISHED", "Unpublished"
        INACTIVE = "INACTIVE", "Inactive"
        PROCESSING = "PROCESSING", "Processing"
        ERROR = "ERROR", "Error"

    name: str = models.CharField(max_length=255, null=False)
    text: str = models.TextField(blank=True)
    price: str = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag, related_name="announcements")
    status: str = models.CharField(max_length=50, blank=True)
    media: "Media"
    note: str = models.TextField(blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.AWAITING_PUBLICATION,
    )
    published_message_link: str = models.CharField(max_length=255, blank=True)
    publication_date: str = models.DateTimeField(null=True)
    unpublished_date: str = models.DateTimeField(null=True, blank=True)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета-класс модели объявления."""

        ordering = ["-publication_date"]
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self) -> str:
        """Строковое представление объявления."""
        return f"Announcement {self.name}. Status: {self.processing_status}. Date: {self.publication_date}"


@deconstructible
class UniquePathAndRename:
    """Класс для генерации уникального имени файла."""

    def __call__(self, instance: "Media", filename: str) -> str:
        """Генерация уникального имени файла при вызове класса."""
        ext = filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        subdir = str(instance.announcement.id)
        return os.path.join(subdir, filename)


content_file_name: UniquePathAndRename = UniquePathAndRename()


class Media(models.Model):
    """Модель медиа-файла."""

    class MediaType(models.TextChoices):
        """Типы медиа-файлов."""

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
        """Мета-класс модели медиа-файла."""

        ordering = ["order"]
        verbose_name = "Медиа-файл"
        verbose_name_plural = "Медиа-файлы"

    def __str__(self) -> str:
        """Строковое представление медиа-файла."""
        return f"Media {self.file} for announcement {self.announcement.name}"
