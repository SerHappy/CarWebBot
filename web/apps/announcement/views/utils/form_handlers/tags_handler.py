from apps.announcement.models import Announcement


def handle_tags(tag_ids: list[str], announcement: Announcement) -> None:
    """Обновляет теги для `announcement` из списка `tag_ids`.

    Args:
        tag_ids (list[str]): Список id тегов.

        announcement (Announcement): Объявление.

    Returns:
        None: None.
    """
    announcement.tags.set(tag_ids)
