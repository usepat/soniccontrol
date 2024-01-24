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

import soniccontrol.utils.constants as const


def setup_logging() -> None:
    config_file: pathlib.Path = const.files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)


setup_logging()
soniccontrol_logger: logging.Logger = logging.getLogger("soniccontrol")
const: ModuleType = const
