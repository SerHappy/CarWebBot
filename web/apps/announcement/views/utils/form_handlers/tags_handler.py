from apps.announcement.models import Announcement


def handle_tags(tag_ids: list[str], announcement: Announcement) -> None:
    announcement.tags.set(tag_ids)
