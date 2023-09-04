import platform

ENCODING: str = "windows-1252" if platform.system() == "Windows" else "utf-8"
