import platform
from pathlib import Path
from typing import Final

import attrs


@attrs.frozen
class _Misc:
    ENCODING: Final[str] = "windows-1252" if platform.system() == "Windows" else "utf-8"
    IMAGE: Final[str] = "image"
    TEXT: Final[str] = "text"
    COMPOUND: Final[str] = "compound"


@attrs.frozen
class _Files:
    # Paths
    SOURCE_DIR: Final[Path] = Path(__file__).parent.parent
    ROOT_DIR: Final[Path] = SOURCE_DIR.parent
    LOG_DIR: Final[Path] = ROOT_DIR / "logs"
    LOGGING_CONFIG: Final[Path] = LOG_DIR / "config.json"
    RESOURCES_DIR: Final[Path] = ROOT_DIR / "resources"
    PICTURES_DIR: Final[Path] = RESOURCES_DIR / "pictures"
    FONTS_DIR: Final[Path] = RESOURCES_DIR / "fonts"
    DOCUMENTS_DIR: Final[Path] = RESOURCES_DIR / "docs"
    CONFIG_JSON: Final[Path] = ROOT_DIR / "config.json"
    SONICCONTROL_LOG: Final[Path] = LOG_DIR / "soniccontrol.log"


@attrs.frozen
class _Events:
    # Events
    RESIZING_EVENT: Final = "<Configure>"
    CONNECTION_ATTEMPT_EVENT: Final = "<<ConnectionAttempt>>"
    DISCONNECTED_EVENT: Final = "<<Disconnected>>"
    SCRIPT_START_EVENT: Final = "<<ScriptStarted>>"
    SCRIPT_STOP_EVENT: Final = "<<ScriptStopped>>"
    FIRMWARE_FLASH_EVENT: Final = "<<FirmwareFlash>>"
    SONICMEASURE_START_EVENT: Final = "<<SonicMeasureStarted>>"
    SONICMEASURE_STOP_EVENT: Final = "<<SonicMeasureStopped>>"
    STATUS_UPDATE_EVENT: Final = "<<StatusUpdate>>"
    MANUAL_MODE_EVENT: Final = "<<ManualMode>>"
    AUTO_MODE_EVENT: Final = "<<AutoMode>>"


@attrs.frozen
class _UIStringsEN:
    HOME_CONTROL_LABEL: Final[str] = "Manual Control"
    FREQ_PLACEHOLDER: Final[str] = "Set Frequency..."
    GAIN_PLACEHOLDER: Final[str] = "Set Gain..."


misc: _Misc = _Misc()
files: _Files = _Files()
events: _Events = _Events()
ui: _UIStringsEN = _UIStringsEN()
