from .models import Announcement
from typing import Literal


def get_status(announcement: Announcement) -> Literal["Снято с публикации", "Опубликовано", "Ожидает публикации"]:
    """Get publication status of a given announcement"""
    if (
        announcement.processing_status == announcement.ProcessingStatus.INACTIVE
        or announcement.processing_status == announcement.ProcessingStatus.UNPUBLISHED
    ):
        return "Снято с публикации"
    if announcement.processing_status == announcement.ProcessingStatus.PUBLISHED:
        return "Опубликовано"
    if announcement.processing_status == announcement.ProcessingStatus.AWAITING_PUBLICATION:
        return "Ожидает публикации"
