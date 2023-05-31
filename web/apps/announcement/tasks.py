from .models import Announcement
from celery import shared_task
from django.utils import timezone
from loguru import logger
from telebot import TeleBot
from decouple import config




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
        message = f"Название: {announcement.name}\nТекст:{announcement.text}\nЦена:{announcement.price}"
        logger.debug("Before sending message")
        bot.send_message(config("CHANNEL_NAME"), message)
        logger.debug("After sending message")
        announcement.is_published = True
        announcement.save()
    logger.debug("After loop")
