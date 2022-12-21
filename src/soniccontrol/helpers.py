import logging
import sys
import os
import json
from PIL import Image

from ttkbootstrap.tooltip import ToolTip as TT
from tkinter import messagebox

import sonicpackage as sp


########################
# Logger configuration #
########################
        
sp.logger.removeHandler(sp.file_handler)
sp.logger.removeHandler(sp.stream_handler)

if not os.path.isdir("logs/"): os.mkdir("logs/")

logger = logging.getLogger("soniccontrol")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
)

file_handler = logging.FileHandler("logs//soniccontrol.log")
file_handler.setFormatter(formatter)

file_handler_sp = logging.FileHandler("logs//sonicpackage.log")
file_handler_sp.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

sp.logger.addHandler(file_handler_sp)
sp.logger.addHandler(stream_handler)


##################################
# Helper Functions Configuration #
##################################

def resize_img(image_path: str, maxsize: tuple) -> Image:
    """
    This function takes an image_path and returns an image object.
    This is used for soniccontrol to initialize images and icons 
    so that tkinter can uses this in the GUI.

    PARAMETERS:
        image_path (str): the path to the said image
        maxsize (tuple): data about the pixel size of the image

    RETURNS:
        image (Image): the Image object that tkinter uses
    """
    image = Image.open(image_path)
    r1 = image.size[0] / maxsize[0]  # width ratio
    r2 = image.size[1] / maxsize[1]  # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image

class ToolTip(TT):
    def __init__(self, *args, **kwargs):
        if not sys.platform == "linux":
            super().__init__(*args, **kwargs)


if __name__ == "__main__":
    pass