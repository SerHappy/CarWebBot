from .models import Announcement
from django.db.models.signals import pre_save
from django.dispatch import receiver
from loguru import logger


@receiver(pre_save, sender=Announcement)
def increment_counter(sender: Announcement, instance: Announcement, **kwargs) -> None:
    """Increment modified counter on Announcement model instance."""
    logger.debug(f"pre_save signal for {instance}")
    if instance.pk is not None:
        logger.debug(f"Modified {instance}. Incrementing counter to {instance.modified_count + 1}")
        instance.modified_count += 1
