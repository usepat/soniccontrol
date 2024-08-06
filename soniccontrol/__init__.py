from __future__ import annotations

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
import os
from ttkbootstrap.utility import enable_high_dpi_awareness
from soniccontrol.utils.files import files
from soniccontrol.utils.system import System, PLATFORM

# create directories if missing
os.makedirs(files.LOG_DIR, exist_ok=True)
os.makedirs(files.DATA_DIR, exist_ok=True)

def setup_logging() -> None:
    config_file: pathlib.Path = files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)

setup_logging()
soniccontrol_logger: logging.Logger = logging.getLogger("soniccontrol")

def check_high_dpi_windows() -> None:
    if PLATFORM == System.WINDOWS:
        enable_high_dpi_awareness()


def setup_fonts() -> None:
    print("Installing fonts...")
    platform: str = sys.platform
    font_files = glob.glob("./resources/fonts/*.ttf")
    try:
        process = subprocess.run(
            [
                rf"./bin/font-install/{platform}/font-install",
                *list(font for font in font_files),
            ],
        )
        if process.returncode != 0:
            raise RuntimeError("Failed to install fonts")
    except Exception:
        soniccontrol_logger.warning("Failed to install fonts", exc_info=True)


check_high_dpi_windows()
setup_fonts()


soniccontrol_logger.info("SonicControl %s", __version__)
soniccontrol_logger.info("Author: %s", __author__)
soniccontrol_logger.info("Email: %s", __email__)
soniccontrol_logger.info("License: %s", __license__)
soniccontrol_logger.info("Status: %s", __status__)
soniccontrol_logger.info("Python: %s", sys.version)
soniccontrol_logger.info("Platform: %s", sys.platform)
