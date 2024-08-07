from __future__ import annotations

import glob
import json
import logging
import logging.config
import pathlib
import subprocess
import sys
import os
from ttkbootstrap.utility import enable_high_dpi_awareness
from async_tkinter_loop import async_mainloop
from soniccontrol_gui.views.core.connection_window import ConnectionWindow
from shared.system import System, PLATFORM
from shared.files import files

# create directories if missing
os.makedirs(files.DATA_DIR, exist_ok=True)
os.makedirs(files.LOG_DIR, exist_ok=True)

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
    font_files = glob.glob(str(files.FONTS_DIR / "*.ttf"))
    try:
        process = subprocess.run(
            [
                files.SOURCE_DIR / rf"gui/bin/font-install/{platform}/font-install",
                *list(font for font in font_files),
            ],
        )
        if process.returncode != 0:
            raise RuntimeError("Failed to install fonts")
    except Exception:
        soniccontrol_logger.warning("Failed to install fonts", exc_info=True)


check_high_dpi_windows()
setup_fonts()

def start_gui(enable_simulation=False):
    main_window = ConnectionWindow(enable_simulation)
    if PLATFORM != System.WINDOWS:
        soniccontrol_logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(main_window.view)
    async_mainloop(main_window.view)

soniccontrol_logger.info("Python: %s", sys.version)
soniccontrol_logger.info("Platform: %s", sys.platform)
