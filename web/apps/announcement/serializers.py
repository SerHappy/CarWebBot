import json


def serialize_media(media_objects) -> str:
    """Сериализует медиа-объекты `media_objects` в JSON."""
    media_json = [
        {
            "media_type": media.media_type,
            "file": media.file.name,
            "announcement": media.announcement.id,
            "order": media.order,
            "size": media.file.size,
        }
        for media in media_objects
    ]
    return json.dumps(media_json)
