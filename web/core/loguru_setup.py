from django.conf import settings


def setup_logger(logger, settings_dict=None) -> None:
    """
    Setup logger with settings from .env file

    All log files are stored in LOGURU_PATH directory.
    Every day at midnight log files are rotated and compressed.
    """
    logger.remove()
    logger.add(
        settings.LOGURU_PATH,
        rotation="0:00",
        enqueue=True,
        compression="zip",
        level=settings.LOGURU_LEVEL,
        format=settings.LOGURU_FORMAT,
        serialize=False,
    )
