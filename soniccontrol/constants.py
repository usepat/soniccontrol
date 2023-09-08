import PIL
from typing import Tuple, Literal
from PIL.ImageTk import PhotoImage
from soniccontrol.utils import resize_img
from pathlib import Path

LOGDIR: Path = Path("logs")
RESOURCES_DIR: Path = Path("resources")
PICTURES_DIR: Path = RESOURCES_DIR / "pictures"
FONTS_DIR: Path = RESOURCES_DIR / "fonts"
DOCUMENTS_DIR: Path = RESOURCES_DIR / "documents"
CONFIG_JSON: Path = Path("config.json")


class Images:
    TAB_ICON_SIZE: Tuple[int, int] = (25, 25)
    BUTTON_ICON_SIZE: Tuple[int, int] = (15, 15)

    REFRESH_IMG_BLACK: Path = PICTURES_DIR / "refresh_icon_black.png"
    REFRESH_IMG_GREY: Path = PICTURES_DIR / "refresh_icon_grey.png"
    REFRESH_IMG_WHITE: Path = PICTURES_DIR / "refresh_icon_white.png"

    HOME_IMG_GREY: Path = PICTURES_DIR / "home_icon_grey.png"
    HOME_IMG_BLACK: Path = PICTURES_DIR / "home_icon_black.png"

    SCRIPT_IMG_BLACK: Path = PICTURES_DIR / "script_icon_black.png"

    INFO_IMG_BLACK: Path = PICTURES_DIR / "info_icon_black.png"
    INFO_IMG_WHITE: Path = PICTURES_DIR / "info_icon_white.png"

    CONNECTION_IMG_BLACK: Path = PICTURES_DIR / "connection_icon_black.png"
    CONNECTION_IMG_WHITE: Path = PICTURES_DIR / "connection_icon_white.png"

    PLAY_IMG_BLACK: Path = PICTURES_DIR / "play_icon_black.png"
    PLAY_IMG_WHITE: Path = PICTURES_DIR / "play_icon_white.png"

    SAVE_ICON_BLACK: Path = PICTURES_DIR / "save_icon_black.png"
    SAVE_ICON_WHITE: Path = PICTURES_DIR / "save_icon_white.png"

    PAUSE_IMG_BLACK: Path = PICTURES_DIR / "pause_icon_black.png"
    PAUSE_IMG_WHITE: Path = PICTURES_DIR / "pause_icon_white.png"

    FORWARDS_IMG_BLACK: Path = PICTURES_DIR / "forwards_icon_black.png"
    FORWARDS_IMG_WHITE: Path = PICTURES_DIR / "forwards_icon_white.png"

    BACK_IMG_BLACK: Path = PICTURES_DIR / "back_icon_black.png"
    BACK_IMG_WHITE: Path = PICTURES_DIR / "back_icon_white.png"

    MENUE_IMG_BLACK: Path = PICTURES_DIR / "menue_icon_black.png"
    MENUE_IMG_WHITE: Path = PICTURES_DIR / "menue_icon_white.png"

    SETTINGS_IMG_BLACK: Path = PICTURES_DIR / "settings_icon_black.png"

    STATUS_IMG_BLACK: Path = PICTURES_DIR / "status_icon_black.png"

    GRAPH_IMG: Path = PICTURES_DIR / "graph_icon.png"

    LINECHART_IMG_BLACK: Path = PICTURES_DIR / "linechart_icon_black.png"

    CONSOLE_IMG_BLACK: Path = PICTURES_DIR / "console_icon_black.png"

    LED_GREEN_IMG: Path = PICTURES_DIR / "led_green_icon.png"
    LED_RED_IMG: Path = PICTURES_DIR / "led_red_icon.png"

    LIGHTNING_IMG_BLACK: Path = PICTURES_DIR / "lightning_icon_black.png"
    LIGHTNING_IMG_WHITE: Path = PICTURES_DIR / "lightning_icon_white.png"

    WAVE_IMG: Path = PICTURES_DIR / "wave_icon.ico"

    @staticmethod
    def get_image(image: Path, size: Tuple[int, int]) -> PhotoImage:
        return PhotoImage(resize_img(image, size))


class Events:
    RESIZING: Literal["<Configure>"] = "<Configure>"
    CONNECTION_ATTEMPT: Literal["<<ConnectionAttempt>>"] = "<<ConnectionAttempt>>"
    DISCONNECTED: Literal["<<Disconnected>>"] = "<<Disconnected>>"
    PORT_REFRESH: Literal["<<PortRefresh>>"] = "<<PortRefresh>>"
    SET_TRD_CONFIG: Literal[
        "<<TransducerConfigurationChanged>>"
    ] = "<<TransducerConfigurationChanged>>"
    SCRIPT_START: Literal["<<ScriptStarted>>"] = "<<ScriptStarted>>"
    SCRIPT_STOP: Literal["<<ScriptStopped>>"] = "<<ScriptStopped>>"
    FIRMWARE_FLASH: Literal["<<FirmwareFlash>>"] = "<<FirmwareFlash>>"
