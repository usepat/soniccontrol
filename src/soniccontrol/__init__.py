import pyglet
import os

lines: list = []

with open("logs//soniccontrol.log") as file:
    lines: list = file.readlines()

if len(lines) > 10000:
    os.remove("logs//soniccontrol.log")
        
with open("logs//sonicpackage.log") as file:
    lines: list = file.readlines()

if len(lines) > 10000:
    os.remove("logs//sonicpackage.log")

pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondExtraLight.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondLight.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondMedium.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBook.otf")
pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBold.otf")

from soniccontrol.core import Root
