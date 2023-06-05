from .views import publish_announcement_to_channel
from apps.announcement.models import Announcement
from celery import shared_task
from core.loguru_setup import setup_logger
from django.utils import timezone
from loguru import logger


setup_logger(logger)


@shared_task
def publish_announcements() -> None:
    logger.info("Publishing announcements...")

    now = timezone.now()
    announcements_to_publish = Announcement.objects.filter(
        publication_date__lte=now,
        is_published=False,
        is_active=True,
        processing_status=Announcement.ProcessingStatus.PENDING,
    )
    logger.info(f"Announcements to publish: {announcements_to_publish.count()}")
    logger.debug("Before loop")
    for announcement in announcements_to_publish:
        announcement.processing_status = Announcement.ProcessingStatus.PROCESSING
        announcement.save()
        logger.debug("Announcement status changed to PROCESSING")
        try:
            publish_announcement_to_channel(announcement)
            logger.debug("Announcement published")
            announcement.processing_status = Announcement.ProcessingStatus.DONE
            announcement.save()
            logger.debug("Announcement status changed to DONE")
        except Exception as e:
            logger.error(f"Error while publishing announcement: {e}")
    logger.debug("After loop")
