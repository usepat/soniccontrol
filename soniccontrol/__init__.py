from __future__ import annotations

from types import ModuleType
from typing import Final

__version__ = "1.9.8"
__author__ = "usePAT G.m.b.H"
__email__ = "info@usepat.com"
__license__ = ""
__maintainer__ = "Ilja Golovanov"
__maintainer_email__ = "ilja.golovanov@usepat.com"
__status__ = "Development"

import glob
import json
import logging
import logging.config
import pathlib
import subprocess
import sys

from soniccontrol.utils.files import files


def setup_logging() -> None:
    config_file: pathlib.Path = files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)


def setup_fonts() -> None:
    print("Installing fonts...")
    platform: str = sys.platform
    font_files = glob.glob("./resources/fonts/*.ttf")
    process = subprocess.run(
        [
            rf"./bin/font-install/{platform}/font-install",
            *list(font for font in font_files),
        ],
    )
    if process.returncode != 0:
        soniccontrol_logger.warning("Failed to install fonts")


setup_logging()
setup_fonts()
soniccontrol_logger: logging.Logger = logging.getLogger("soniccontrol")

soniccontrol_logger.info("SonicControl %s", __version__)
soniccontrol_logger.info("Author: %s", __author__)
soniccontrol_logger.info("Email: %s", __email__)
soniccontrol_logger.info("License: %s", __license__)
soniccontrol_logger.info("Status: %s", __status__)
soniccontrol_logger.info("Python: %s", sys.version)
soniccontrol_logger.info("Platform: %s", sys.platform)
