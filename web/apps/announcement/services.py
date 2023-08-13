from .models import Announcement
from typing import Literal


def get_status(
    announcement: Announcement,
) -> Literal[
    "Не было опубликовано",
    "Снято с публикации",
    "Опубликовано",
    "Ожидает публикации",
    "Ошибка публикации",
    "Неизвестный статус",
]:
    """Get publication status of a given announcement"""
    match announcement.processing_status:
        case announcement.ProcessingStatus.INACTIVE:
            return "Не было опубликовано"
        case announcement.ProcessingStatus.UNPUBLISHED:
            return "Снято с публикации"
        case announcement.ProcessingStatus.PUBLISHED:
            return "Опубликовано"
        case announcement.ProcessingStatus.AWAITING_PUBLICATION:
            return "Ожидает публикации"
        case announcement.ProcessingStatus.PROCESSING:
            return "Ожидает публикации"
        case announcement.ProcessingStatus.ERROR:
            return "Ошибка публикации"
        case _:
            return "Неизвестный статус"
