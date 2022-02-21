from PIL import Image, ImageTk


def resize_img(image_path, maxsize):
    image = Image.open(image_path)
    r1 = image.size[0]/maxsize[0] # width ratio
    r2 = image.size[1]/maxsize[1] # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0]/ratio), int(image.size[1]/ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image


# Defining images
# Uses custom resize funtion in helpers file
refresh_img: object = ImageTk.PhotoImage(resize_img('pictures//refresh_icon.png', (20, 20)))
home_img: object = ImageTk.PhotoImage(resize_img('pictures//home_icon.png', (30, 30)))
script_img: object = ImageTk.PhotoImage(resize_img('pictures//script_icon.png', (30, 30)))
connection_img: object = ImageTk.PhotoImage(resize_img('pictures//connection_icon.png', (30, 30)))
info_img: object = ImageTk.PhotoImage(resize_img('pictures//info_icon.png', (30, 30)))
play_img: object = ImageTk.PhotoImage(resize_img('pictures//play_icon.png', (30, 30)))
pause_img: object = ImageTk.PhotoImage(resize_img('pictures//pause_icon.png', (30, 30)))
wave_bg: object = ImageTk.PhotoImage(resize_img('pictures//wave_bg.png', (540,440)))
graph_img: object = ImageTk.PhotoImage(resize_img('pictures//graph.png', (100,100)))
led_green_img: object = ImageTk.PhotoImage(resize_img('pictures//led_green.png', (35,35)))
led_red_img: object = ImageTk.PhotoImage(resize_img('pictures//led_red.png', (35,35)))