from apps.announcement.models import Announcement


def handle_tags(tag_str: str, announcement: Announcement) -> None:
    tag_ids = sorted(tag_str.split(",") if tag_str else [])
    announcement.tags.set(tag_ids)
