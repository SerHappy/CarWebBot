from .models import Announcement
from typing import Literal


def get_status(announcement: Announcement) -> Literal["Снято с публикации", "Опубликовано", "Ожидает публикации"]:
    """Get publication status of a given announcement"""
    if not announcement.is_active:
        return "Снято с публикации"
    if announcement.is_published:
        return "Опубликовано"
    if not announcement.is_published:
        return "Ожидает публикации"
