import logging
import os
import sys


def configure_logging():
    logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.getLevelName(logging_level))
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger

def get_logger():
    # Just for a better name
    return configure_logging()