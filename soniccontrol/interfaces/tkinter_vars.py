import ttkbootstrap as ttk
from tkinter import Misc
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RootStringVar(ttk.StringVar):
    def __init__(
        self,
        master: Misc | None = None,
        value: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(master, value, name)
        self.master = master
        self.dot_position: int = 0
        self.dot_text: str = "   "
        self.is_dot_animation_running: bool = False
        self.original_text: str = self.get()

    def animate_dots(self, text: str = "") -> None:
        self.is_dot_animation_running = True
        self.dot_animator(text=text)

    def stop_animation_of_dots(self) -> None:
        self.is_dot_animation_running = False

    def dot_animator(self, text: Optional[str] = None) -> None:
        if not self.is_dot_animation_running:
            return
        logger.debug("running dot animation...")
        if text is not None:
            self.original_text = text
        if self.dot_position > 3:
            self.dot_position = 0
        logger.debug(
            f"with text {self.original_text} and boolean {self.is_dot_animation_running} and {self.dot_position} position"
        )

        self.dot_text = "." * self.dot_position + " " * (3 - self.dot_position)
        self.dot_text = f"{self.original_text}{self.dot_text}"

        logger.debug(self.dot_text)
        self.set(self.dot_text)
        self.dot_position += 1
        self.master.after(500, self.dot_animator)
