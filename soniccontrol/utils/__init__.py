import PIL


# pictures
def resize_img(image_path: str, maxsize: tuple) -> PIL.Image:
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
    image = PIL.Image.open(image_path)
    r1 = image.size[0] / maxsize[0]  # width ratio
    r2 = image.size[1] / maxsize[1]  # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, PIL.Image.ANTIALIAS)
    return image
