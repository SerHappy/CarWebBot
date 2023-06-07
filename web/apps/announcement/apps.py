from django.apps import AppConfig


class AnnouncementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.announcement"

    def ready(self) -> None:
        import apps.announcement.signals  # noqa
