from .models import Announcement
from django.utils import timezone
from typing import Literal


def get_status(announcement: Announcement) -> Literal["Снято с публикации", "Опубликовано", "Ожидает публикации"]:
    """Get publication status of a given announcement"""
    if not announcement.is_active:
        return "Снято с публикации"
    if announcement.is_published:
        return "Опубликовано в "
    if not announcement.is_published:
        return "Ожидает публикации"
