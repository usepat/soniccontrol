from __future__ import annotations

import pathlib
# from asyncio import Lock
from threading import Lock

import ttkbootstrap as ttk


def give_image(image: pathlib.Path, sizing: tuple[int, int]) -> ttk.ImageTk.PhotoImage:
    return ttk.ImageTk.PhotoImage(ttk.Image.open(image).resize(sizing))


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
        cls, image_path: pathlib.Path, sizing: tuple[int, int]
    ) -> str:
        return f"{image_path}{sizing}"

    @classmethod
    def _load_image(
        cls, image: pathlib.Path, sizing: tuple[int, int]
    ) -> ttk.ImageTk.PhotoImage:
        return ttk.ImageTk.PhotoImage(ttk.Image.open(image).resize(sizing))

    @classmethod
    def load_image(
        cls, image_path: pathlib.Path, sizing: tuple[int, int]
    ) -> ttk.ImageTk.PhotoImage:
        if cls._master is None:
            raise RuntimeError("master not initialized")
        key: str = cls.generate_image_key(image_path, sizing)
        if key not in cls.images:
            cls.images[key] = cls._load_image(image_path, sizing)
        return cls.images[key]
