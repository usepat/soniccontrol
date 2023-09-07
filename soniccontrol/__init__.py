from __future__ import annotations

__version__ = "1.9.7"
__author__ = "usePAT G.m.b.H"
__email__ = "info@usepat.com"
__license__ = ""
__maintainer__ = "Ilja Golovanov"
__maintainer_email__ = "ilja.golovanov@usepat.com"
__status__ = "Development"

import logging
import sys
import os

try:
    MAX_LINES: int = 10000
    lines: int = 0

    with open("logs//soniccontrol.log") as file:
        lines: int = len(file.readlines())
    if lines > MAX_LINES:
        os.remove("logs//soniccontrol.log")

    with open("logs//sonicpackage.log") as file:
        lines: int = len(file.readlines())
    if lines > MAX_LINES:
        os.remove("logs//sonicpackage.log")

except FileNotFoundError as fe:
    print("File not found, proceeding...")

if not os.path.isdir("logs/"):
    os.mkdir("logs/")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
)

file_handler = logging.FileHandler("logs/soniccontrol.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

from soniccontrol.core import SonicControl
