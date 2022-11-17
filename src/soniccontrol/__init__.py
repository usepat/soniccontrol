import pyglet
import os

try:
    lines: list = []

    with open("logs//soniccontrol.log") as file:
        lines: list = file.readlines()

    if len(lines) > 10000:
        os.remove("logs//soniccontrol.log")
            
    with open("logs//sonicpackage.log") as file:
        lines: list = file.readlines()

    if len(lines) > 10000:
        os.remove("logs//sonicpackage.log")

except FileNotFoundError as fe:
    print("File not found, proceeding...")
    pass

pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondExtraLight.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondLight.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondMedium.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBook.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBold.otf")

from soniccontrol.core import Root
