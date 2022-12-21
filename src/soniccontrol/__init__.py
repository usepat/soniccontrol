import pyglet
import os

try:
    MAX_LINES: int = 10000
    lines: int = 0

    with open("logs//soniccontrol.log") as file:
        lines: int = len(file.readlines())
    if lines > MAX_LINES:
        os.remove("logs//soniccontrol.log")
            
    with open("logs//sonicpackage.log") as file:
        lines: int = len(file.readlines())
    if lines > MAX_LINES:
        os.remove("logs//sonicpackage.log")

except FileNotFoundError as fe:
    print("File not found, proceeding...")

finally:
    pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondExtraLight.otf")
    pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondLight.otf")
    pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondMedium.otf")
    pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBook.otf")
    pyglet.font.add_file("src//soniccontrol//fonts//QTypeOT-CondBold.otf")

    from soniccontrol.core import Root