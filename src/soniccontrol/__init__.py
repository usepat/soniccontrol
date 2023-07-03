import os
import pyglet
import soniccontrol.constants as const
from soniccontrol.interfaces import Root
from soniccontrol.core import SonicControl, LightWeightSonicControl


def folder_cleaner(folder_path, condition_function):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if condition_function(file_path):
                os.remove(file_path)


def should_clean_log(file_path, max_lines):
    with open(file_path) as file:
        return len(file.readlines()) > max_lines


class GUIBuilder:
    @classmethod
    def build(cls, light_weight: bool) -> Root:
        cls.setup()
        return LightWeightSonicControl() if light_weight else SonicControl()

    @staticmethod
    def setup() -> None:
        try:
            folder_cleaner(const.LOGFOLDER_PATH, const.MAX_LOG_LINES)
        except FileNotFoundError as fe:
            print("Logfiles not found, creating new ones and proceeding further...")
        finally:
            pyglet.font.add_file("resources//fonts//QTypeOT-CondExtraLight.otf")
            pyglet.font.add_file("resources//fonts//QTypeOT-CondLight.otf")
            pyglet.font.add_file("resources//fonts//QTypeOT-CondMedium.otf")
            pyglet.font.add_file("resources//fonts//QTypeOT-CondBook.otf")
            pyglet.font.add_file("resources//fonts//QTypeOT-CondBold.otf")
