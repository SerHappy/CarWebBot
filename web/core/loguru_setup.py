from decouple import config
from loguru._defaults import LOGURU_FORMAT


def setup_logger(logger, settings_dict=None) -> None:
    """
    Setup logger with settings from .env file

    All log files are stored in LOGURU_PATH directory.
    Every day at midnight log files are rotated and compressed.
    """
    logger.remove()
    logger.add(
        config("LOGURU_PATH"),
        rotation="0:00",
        enqueue=True,
        compression="zip",
        level=config("LOGURU_LEVEL", default="DEBUG"),
        format=config("LOGURU_FORMAT", default=LOGURU_FORMAT),
        # colorize=config("LOGURU_COLORIZE", default=True, cast=bool),
        serialize=config("LOGURU_SERIALIZE", default=False, cast=bool),
        # diagnose=config("LOGURU_DIAGNOSE", default=True, cast=bool),
        # backtrace=config("LOGURU_BACKTRACE", default=True, cast=bool),
    )
