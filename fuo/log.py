import logging
import os
from logging.handlers import RotatingFileHandler
from typing import List

from fuo import config


def init(root: bool = True):
    stream_handler = logging.StreamHandler()

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir, exist_ok=True)
    log_file = os.path.join(config.log_dir, "fuo.log")
    file_handler = RotatingFileHandler(
        log_file,
        encoding="utf-8",
        delay=True,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
    )

    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if root:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger("fuo")

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(config.log_level)
