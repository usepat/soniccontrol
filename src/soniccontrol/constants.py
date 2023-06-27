from PIL import Image
from soniccontrol.helpers import resize_img

REFRESH_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//refresh_icon.png", (20, 20)
)
HOME_RAW_IMG: Image = resize_img("src//soniccontrol//pictures//home_icon.png", (30, 30))
SCRIPT_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//script_icon.png", (30, 30)
)
CONNECTION_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//connection_icon.png", (30, 30)
)
INFO_RAW_IMG: Image = resize_img("src//soniccontrol//pictures//info_icon.png", (30, 30))
PLAY_RAW_IMG: Image = resize_img("src//soniccontrol//pictures//play_icon.png", (30, 30))
PAUSE_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//pause_icon.png", (30, 30)
)
WAVE_RAW_IMG: Image = resize_img("src//soniccontrol//pictures//wave_bg.png", (540, 440))
GRAPH_RAW_IMG: Image = resize_img("src//soniccontrol//pictures//graph.png", (100, 100))
LED_GREEN_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//led_green.png", (35, 35)
)
LED_RED_RAW_IMG: Image = resize_img(
    "src//soniccontrol//pictures//led_red.png", (35, 35)
)

MAX_NEGATIVE_TEMP: int = 50
MAX_POSITIVE_TEMP: int = 300
DIVIDE_TO_KHZ: int = 1000

CONFIGPATH: str = "config.json"
VERSION: str = "1.9.6"

if __name__ == "__main__":
    pass
