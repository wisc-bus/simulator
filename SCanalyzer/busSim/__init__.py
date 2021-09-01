from .busSim import BusSim
from .config import Config

import logging
import sys

LOG_FILE_PATH = "busSim.log"


def _init_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)

    # log everything to the log file; log WARNING+ to stderr
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(LOG_FILE_PATH, "w")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

_init_logger()
