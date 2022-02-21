from PIL import Image


def resize_img(image_path: str, maxsize: tuple) -> Image:
    image = Image.open(image_path)
    r1 = image.size[0]/maxsize[0] # width ratio
    r2 = image.size[1]/maxsize[1] # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0]/ratio), int(image.size[1]/ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image


# Defining images
# Uses custom resize funtion in helpers file
refresh_img: Image = resize_img('soniccontrol//pictures//refresh_icon.png', (20, 20))
home_img: Image = resize_img('soniccontrol//pictures//home_icon.png', (30, 30))
script_img: Image = resize_img('soniccontrol//pictures//script_icon.png', (30, 30))
connection_img: Image = resize_img('soniccontrol//pictures//connection_icon.png', (30, 30))
info_img: Image = resize_img('soniccontrol//pictures//info_icon.png', (30, 30))
play_img: Image = resize_img('soniccontrol//pictures//play_icon.png', (30, 30))
pause_img: Image = resize_img('soniccontrol//pictures//pause_icon.png', (30, 30))
wave_bg: Image = resize_img('soniccontrol//pictures//wave_bg.png', (540,440))
graph_img: Image = resize_img('soniccontrol//pictures//graph.png', (100,100))
led_green_img: Image = resize_img('soniccontrol//pictures//led_green.png', (35,35))
led_red_img: Image = resize_img('soniccontrol//pictures//led_red.png', (35,35))