import ttkbootstrap as ttk
from icecream import ic


class StringVar(ttk.StringVar):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._master: ttk.tk.Widget | None = None
        self._dot_threshold_idx: int = 0
        self._dot_string: str = "   "
        self._is_animation_running: bool = False
        self._original_string: str = self.get()

    def animate_dots(self, master: ttk.ttk.Widget, text: str | None = None) -> None:
        self._master = master
        self._is_animation_running = True
        self._original_string = text if text is not None else self.get()
        self._dot_animator()

    def stop_animation(self) -> None:
        self._is_animation_running = False
        self.set(self._original_string)

    def _dot_animator(self):
        if not self._is_animation_running or self._master is None:
            ic(self._is_animation_running, self._master)
            return
        if self._dot_threshold_idx > 3:
            self._dot_threshold_idx = 0

        self._dot_string = "." * self._dot_threshold_idx + " " * (
            3 - self._dot_threshold_idx
        )
        self._dot_string = f"{self._original_string}{self._dot_string}"

        self.set(self._dot_string)
        self._dot_threshold_idx += 1
        self._master.after(500, self._dot_animator)
