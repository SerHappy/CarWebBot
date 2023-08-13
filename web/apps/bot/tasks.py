from .views import delete_announcement_from_channel
from .views import publish_announcement_to_channel
from apps.announcement.models import Announcement
from apps.settings.models import Setting
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
        processing_status=Announcement.ProcessingStatus.AWAITING_PUBLICATION,
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
            announcement.processing_status = Announcement.ProcessingStatus.PUBLISHED
            announcement.unpublished_date = None
            announcement.save()
            logger.debug("Announcement status changed to PUBLISHED")
        except Exception as e:
            logger.error(f"Error while publishing announcement: {e}")
            announcement.processing_status = Announcement.ProcessingStatus.ERROR
            announcement.save()
            logger.debug("Announcement status changed to ERROR")
    logger.debug("After loop")


@shared_task
def unpublish_announcements() -> None:
    logger.info("Unpublishing old announcements...")
    settings = Setting.objects.first()
    if settings is None:
        logger.info("Unpublish date is not set, skipping...")
        return
    if settings.unpublish_date is None:
        logger.info("Unpublish date is not set, skipping...")
        return
    unpublish_date = settings.unpublish_date
    announcements_to_unpublish = Announcement.objects.filter(
        publication_date__lte=unpublish_date,
        processing_status=Announcement.ProcessingStatus.PUBLISHED,
    )
    logger.debug(f"Unpublish date: {unpublish_date}")
    logger.debug(f"Announcements to unpublish: {announcements_to_unpublish}")
    if announcements_to_unpublish.count() == 0:
        logger.info("No announcements to unpublish")
        return
    logger.info(f"Announcements to unpublish: {announcements_to_unpublish.count()}")
    logger.debug("Before loop")
    for announcement in announcements_to_unpublish:
        announcement.processing_status = Announcement.ProcessingStatus.PROCESSING
        announcement.save()
        try:
            delete_announcement_from_channel(announcement)
            announcement.processing_status = Announcement.ProcessingStatus.UNPUBLISHED
            announcement.unpublished_date = timezone.now()
            announcement.save()
        except Exception as e:
            logger.error(f"Error while unpublishing announcement: {e}")
            announcement.processing_status = Announcement.ProcessingStatus.ERROR
            announcement.save()
    logger.debug("After loop")
