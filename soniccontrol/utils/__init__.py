import pathlib

import ttkbootstrap as ttk


def give_image(image: pathlib.Path, sizing: tuple[int, int]) -> ttk.ImageTk.PhotoImage:
    return ttk.ImageTk.PhotoImage(ttk.Image.open(image).resize(sizing))
