from pathlib import Path
from typing import Final

import attrs


@attrs.frozen
class _Files:
    SOURCE_DIR: Final[Path] = Path(__file__).parent.parent
    ROOT_DIR: Final[Path] = SOURCE_DIR.parent
    BIN_DIR: Final[Path] = ROOT_DIR / "bin"
    LOG_DIR: Final[Path] = ROOT_DIR / "logs"
    LOGGING_CONFIG: Final[Path] = ROOT_DIR / "log_config.json"
    RESOURCES_DIR: Final[Path] = ROOT_DIR / "resources"
    PICTURES_DIR: Final[Path] = RESOURCES_DIR / "pictures"
    FONTS_DIR: Final[Path] = RESOURCES_DIR / "fonts"
    DOCUMENTS_DIR: Final[Path] = RESOURCES_DIR / "docs"
    CONFIG_JSON: Final[Path] = ROOT_DIR / "config.json"
    SONICCONTROL_LOG: Final[Path] = LOG_DIR / "soniccontrol.log"
    CLI_MVC_MOCK: Final[Path] = BIN_DIR / "cli_simulation_mvp"
    AVRDUDE: Final[Path] = BIN_DIR / "avrdude"
    TEXT_DIR: Final[Path] = RESOURCES_DIR / "texts"
    HELPTEXT_SONIC_V1: Final[Path] = TEXT_DIR / "helpttext_sonic_v1.md"
    HELPTEXT_INTERNAL_COMMANDS: Final[Path] = TEXT_DIR /  "helptext_internal_commands.md"


files: _Files = _Files()


@attrs.frozen
class _Images:
    HOME_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "home_icon_black.png"
    BACK_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "back_icon_white.png"
    BACK_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "back_icon_black.png"
    CONNECTION_ICON_BLACK: Final[Path] = (
        files.PICTURES_DIR / "connection_icon_black.png"
    )
    CONNECTION_ICON_WHITE: Final[Path] = (
        files.PICTURES_DIR / "connection_icon_white.png"
    )
    CONSOLE_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "console_icon_black.png"
    SCRIPT_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "script_icon_black.png"
    SETTINGS_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "settings_icon_black.png"
    STATUS_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "status_icon_black.png"
    FORWARDS_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "forwards_icon_black.png"
    FORWARDS_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "forwards_icon_white.png"
    INFO_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "info_icon_black.png"
    INFO_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "info_icon_white.png"
    LED_ICON_GREEN: Final[Path] = files.PICTURES_DIR / "led_green_icon.png"
    LED_ICON_RED: Final[Path] = files.PICTURES_DIR / "led_red_icon.png"
    LIGHTNING_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "lightning_icon_white.png"
    LINECHART_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "linechart_icon_black.png"
    MENUE_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "menue_icon_black.png"
    MENUE_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "menue_icon_white.png"
    PAUSE_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "pause_icon_black.png"
    PAUSE_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "pause_icon_white.png"
    PLAY_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "play_icon_black.png"
    PLAY_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "play_icon_white.png"
    REFRESH_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "refresh_icon_white.png"
    REFRESH_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "refresh_icon_black.png"
    REFRESH_ICON_GREY: Final[Path] = files.PICTURES_DIR / "refresh_icon_grey.png"
    SAVE_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "save_icon_black.png"
    SAVE_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "save_icon_white.png"
    END_ICON_WHITE: Final[Path] = files.PICTURES_DIR / "end_icon_white.png"
    END_ICON_BLACK: Final[Path] = files.PICTURES_DIR / "end_icon_black.png"

    HOME_CONTROL_PANEL: Final[Path] = files.PICTURES_DIR / "home_control_panel.png"
    HOME_SIGNAL_CONTROL_PANEL: Final[Path] = (
        files.PICTURES_DIR / "home_signal_control_panel.png"
    )


images: _Images = _Images()
