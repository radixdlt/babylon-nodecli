import logging
from os import getenv


def get_logger(name: str):
    logger = logging.getLogger(name)
    log_level = getenv("LOG_LEVEL", logging.INFO)
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
