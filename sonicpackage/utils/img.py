from PIL import Image

def resize_img(image_path, maxsize):
    image = Image.open(image_path)
    r1 = image.size[0]/maxsize[0] # width ratio
    r2 = image.size[1]/maxsize[1] # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0]/ratio), int(image.size[1]/ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image