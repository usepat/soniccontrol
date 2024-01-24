import ttkbootstrap as ttk


class StringVar(ttk.StringVar):
    def __init__(
        self,
        master: ttk.tk.Widget,
        value: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(master, value, name)
        self._master: ttk.tk.Widget = master
        self._dot_threshold_idx: int = 0
        self._dot_string: str = "   "
        self._is_animation_running: bool = False
        self._original_string: str = self.get()

    def animate_dots(self, text: str = "") -> None:
        self._is_animation_running = True
        self._original_string = text if text is not None else self._original_string
        self._dot_animator()

    def _dot_animator(self):
        if not self._is_animation_running:
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
