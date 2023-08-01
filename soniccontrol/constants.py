import PIL
from soniccontrol.utils import resize_img

REFRESH_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//refresh_icon.png", (20, 20)
)
HOME_RAW_IMG: PIL.Image = resize_img("resources//pictures//home_icon.png", (20, 20))
SCRIPT_RAW_IMG: PIL.Image = resize_img("resources//pictures//script_icon.png", (20, 20))
CONNECTION_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//connection_icon.png", (20, 20)
)
INFO_RAW_IMG: PIL.Image = resize_img("resources//pictures//info_icon.png", (20, 20))
PLAY_RAW_IMG: PIL.Image = resize_img("resources//pictures//play_icon.png", (15, 15))
PAUSE_RAW_IMG: PIL.Image = resize_img("resources//pictures//pause_icon.png", (20, 20))
WAVE_RAW_IMG: PIL.Image = resize_img("resources//pictures//wave_bg.png", (540, 440))
GRAPH_RAW_IMG: PIL.Image = resize_img("resources//pictures//graph.png", (100, 100))
LED_GREEN_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//led_green.png", (20, 20)
)
SETTINGS_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//settings_icon.png", (20, 20)
)
STATUS_RAW_IMG: PIL.Image = resize_img("resources//pictures//status_icon.png", (20, 20))
CONSOLE_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//console_icon.png", (25, 25)
)
SONIC_MEASURE_RAW_IMG: PIL.Image = resize_img(
    "resources//pictures//line_chart_icon.png", (20, 20)
)
MENUE_RAW_IMG: PIL.Image = resize_img('resources//pictures//menue.png', (15, 15))


class Events:
    RESIZING: str = '<Configure>'
    CONNECTION_ATTEMPT: str = '<<ConnectionAttempt>>'
    DISCONNECTED: str = '<<Disconnected>>'
    PORT_REFRESH: str = '<<PortRefresh>>'
    SET_VALUES: str = '<<SetValues>>'
    SET_FREQ: str = '<<SetFrequency>>'
    SET_GAIN: str = '<<SetGain>>'
    SET_TRD_CONFIG: str = '<<TransducerConfigurationChanged>>'
    START_SCRIPT: str = '<<ScriptStarted>>'
    STOP_SCRIPT: str = '<<ScriptStopped>>'