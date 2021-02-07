from .busSim import BusSim

import logging
import sys

LOG_FILE_PATH = "busSim.log"


def _init_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)

    # init file handler
    handler = logging.FileHandler(LOG_FILE_PATH)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


_init_logger()
