from django.conf import settings
from loguru import Logger
from typing import Any

import os


def setup_logger(logger: Logger, logger_settings: Any = None) -> None:
    """
    Set up logger with settings from .env file.

    All log files are stored in LOGURU_FOLDER directory.
    Every day at midnight log files are rotated and compressed.
    """
    logger.remove()
    logger.add(
        os.path.join(settings.LOGURU_FOLDER, "all/server.log"),
        rotation="0:00",
        enqueue=True,
        compression="zip",
        level=settings.LOGURU_LEVEL,
        format=settings.LOGURU_FORMAT,
        serialize=False,
    )
    logger.add(
        os.path.join(settings.LOGURU_FOLDER, "warnings/server.log"),
        rotation="0:00",
        enqueue=True,
        compression="zip",
        level="WARNING",
        format=settings.LOGURU_FORMAT,
        serialize=False,
    )
