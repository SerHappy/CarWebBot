from .models import Media

import json


def serialize_media(media_objects: list[Media]) -> str:
    """Сериализует медиа-объекты `media_objects` в JSON."""
    media_json = [
        {
            "media_type": media.media_type,
            "file": media.file.name,  # type: ignore[attr-defined]
            "announcement": media.announcement.id,
            "order": media.order,
            "size": media.file.size,  # type: ignore[attr-defined]
        }
        for media in media_objects
    ]
    return json.dumps(media_json)
