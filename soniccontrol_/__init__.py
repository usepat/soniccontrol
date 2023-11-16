from __future__ import annotations

__version__ = "1.9.7"
__author__ = "usePAT G.m.b.H"
__email__ = "info@usepat.com"
__license__ = ""
__maintainer__ = "Ilja Golovanov"
__maintainer_email__ = "ilja.golovanov@usepat.com"
__status__ = "Development"

import logging
from logging.handlers import RotatingFileHandler
import sys
from icecream import install
import soniccontrol.constants as const

install()

if not const.LOG_DIR.exists() or not const.LOG_DIR.is_dir():
    const.LOG_DIR.mkdir(parents=True, exist_ok=True)
    print("Logs directory created.")
else:
    print("Logs directory already exists.")

MAX_SIZE = 0x1_000_000  # 16 megabyte
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
)

file_handler = RotatingFileHandler(
    const.SONICCONTROL_LOG, maxBytes=MAX_SIZE, backupCount=10
)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

from soniccontrol.core import SonicControl

