from __future__ import annotations

import pathlib
from threading import Lock

import ttkbootstrap as ttk

from soniccontrol_gui.resources import resources
from importlib.resources import as_file


class SingletonMeta(type):
    _instances: dict[SingletonMeta, object] = dict()
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ImageLoader(metaclass=SingletonMeta):
    _master: ttk.Window | None = None
    images: dict[str, ttk.ImageTk.PhotoImage] = {}

    def __init__(self, master: ttk.Window | None) -> None:
        if master is None and self._master is None:
            print("No master specified, not initializing ImageLoader")
            return
        elif self._master is None and isinstance(master, ttk.Window):
            self.initialize(master)

    @classmethod
    def initialize(cls, master: ttk.Window) -> type[ImageLoader]:
        cls._master = master
        return cls

    @classmethod
    def generate_image_key(
        cls, image_name: str, sizing: tuple[int, int]
    ) -> str:
        return f"{image_name}{sizing}"

    @classmethod
    def _load_image_resource(
        cls, image_name: str, sizing: tuple[int, int]
    ) -> ttk.ImageTk.PhotoImage:
        with as_file(resources.PICTURES.joinpath(image_name)) as image:
            bytes = image.read_bytes()
            tk_image = ttk.Image.open(image, "r").resize(sizing)
            return ttk.ImageTk.PhotoImage(image=tk_image)

    @classmethod
    def load_image_resource(
        cls, image_name: str, sizing: tuple[int, int]
    ) -> ttk.ImageTk.PhotoImage:
        if cls._master is None:
            raise RuntimeError("master not initialized")
        key: str = cls.generate_image_key(image_name, sizing)
        if key not in cls.images:
            cls.images[key] = cls._load_image_resource(image_name, sizing)
        return cls.images[key]
