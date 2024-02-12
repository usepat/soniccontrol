from __future__ import annotations

from types import ModuleType

__version__ = "1.9.8"
__author__ = "usePAT G.m.b.H"
__email__ = "info@usepat.com"
__license__ = ""
__maintainer__ = "Ilja Golovanov"
__maintainer_email__ = "ilja.golovanov@usepat.com"
__status__ = "Development"

import json
import logging
import logging.config
import pathlib
import subprocess
import sys

from ttkbootstrap.utility import enable_high_dpi_awareness

import soniccontrol.utils.constants as const


def setup_logging() -> None:
    config_file: pathlib.Path = const.files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)


def check_high_dpi_windows() -> None:
    if sys.platform == "":
        enable_high_dpi_awareness()


def setup_fonts() -> None:
    # TODO: Found a go application that installs fonts crossplatdform. Try to utilize it.
    # TODO: Make sure the paths are correct set, because of the name
    print("Installing fonts...")
    platform: str = sys.platform
    process: subprocess.CompletedProcess = subprocess.run(
        [rf"./bin/font-install/{platform}/font-install", r"./resources/fonts/*.ttf"],
    )
    if process.returncode != 0:
        soniccontrol_logger.warning("Failed to install fonts")


setup_logging()
check_high_dpi_windows()
# setup_fonts()
soniccontrol_logger: logging.Logger = logging.getLogger("soniccontrol")
const: ModuleType = const

soniccontrol_logger.info("SonicControl %s", __version__)
soniccontrol_logger.info("Author: %s", __author__)
soniccontrol_logger.info("Email: %s", __email__)
soniccontrol_logger.info("License: %s", __license__)
soniccontrol_logger.info("Status: %s", __status__)
soniccontrol_logger.info("Python: %s", sys.version)
soniccontrol_logger.info("Platform: %s", sys.platform)
