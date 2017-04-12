import logging
import sys

from colorlog import ColoredFormatter

# suppress updater's logs
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
# suppress warnings from googleapi about file_cache
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = " %(log_color)s%(asctime)-6s:%(levelname)-6s%(reset)s | %(log_color)s%(name)s : %(message)s%(reset)s"

formatter = ColoredFormatter(LOG_FORMAT)
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(formatter)
log = logging.getLogger('')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

log.info("Loggers are configured")


def get_logger(name: str):
    return logging.getLogger(name)
