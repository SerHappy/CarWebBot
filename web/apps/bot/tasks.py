from .views import publish_announcement_to_channel
from apps.announcement.models import Announcement
from celery import shared_task
from decouple import config
from django.utils import timezone
from loguru import logger
from telebot import TeleBot


@shared_task
def publish_announcements() -> None:
    logger.info("Publishing announcements...")
    bot = TeleBot(config("TELEGRAM_BOT_TOKEN"))

    now = timezone.now()
    announcements_to_publish = Announcement.objects.filter(
        is_published=False, publication_date__lte=now, is_active=True
    )
    logger.info(f"Announcements to publish: {announcements_to_publish.count()}")
    logger.debug("Before loop")
    for announcement in announcements_to_publish:
        publish_announcement_to_channel(announcement)
    logger.debug("After loop")
