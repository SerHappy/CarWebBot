from django.db import models
from django.utils.deconstruct import deconstructible

import os
import uuid


class Tag(models.Model):
    name: str = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Tag {self.name}"


class Announcement(models.Model):
    name: str = models.CharField(max_length=255, null=False)
    text: str = models.TextField(null=True)
    price: str = models.CharField(max_length=255, null=True)
    tags = models.ManyToManyField(Tag, related_name="announcements")
    status: str = models.CharField(max_length=50, null=True)
    media: "Media"
    note: str = models.TextField(null=True)
    publication_date: str = models.DateTimeField(auto_now_add=False, null=True)
    is_published: bool = models.BooleanField(default=False)
    is_active: bool = models.BooleanField(default=True)

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        return f"Announcement {self.name}. Published: {self.is_published}. Date: {self.publication_date}"


@deconstructible
class UniquePathAndRename(object):
    def __call__(self, instance: "Media", filename: str) -> str:
        ext = filename.split(".")[-1]  # Получаем расширение файла
        # Устанавливаем новое имя файла
        filename = f"{uuid.uuid4()}.{ext}"
        # Используем ID объявления для создания подпапки
        subdir = str(instance.announcement.id)
        # Возвращаем путь к файлу
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

    def __str__(self) -> str:
        return f"Media {self.file} for announcement {self.announcement.name}"
