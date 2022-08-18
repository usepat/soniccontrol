import logging
import sys
from PIL import Image

import sonicpackage as sp

logger = logging.getLogger("soniccontrol")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
)

file_handler = logging.FileHandler("Logs//soniccontrol.log")
file_handler.setFormatter(formatter)

file_handler_sp = logging.FileHandler("Logs//sonicpackage.log")
file_handler_sp.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sp.logger.removeHandler(sp.file_handler)
sp.logger.addHandler(file_handler_sp)
sp.logger.addHandler(stream_handler)

def resize_img(image_path: str, maxsize: tuple) -> Image:
    image = Image.open(image_path)
    r1 = image.size[0] / maxsize[0]  # width ratio
    r2 = image.size[1] / maxsize[1]  # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image