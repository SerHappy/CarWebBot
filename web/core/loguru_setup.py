from decouple import config


def setup_logger(logger, settings_dict=None) -> None:
    logger.remove()
    logger.add(
        config("LOGURU_PATH"),
        rotation="500 MB",
        enqueue=True,
        compression="zip",
        level=config("LOGURU_LEVEL"),
    )
