import soniccontrol.utils.constants as const
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout

from soniccontrol import utils


class ATK_Frame(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, label: str, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._label: ttk.Label = ttk.Label(self, text=label)
        self._spinbox: ttk.Spinbox = ttk.Spinbox(self)

    def publish(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._label.grid(row=0, column=0, padx=5, pady=5)
        self._spinbox.grid(row=0, column=1, padx=5, pady=5)


class SettingsView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        # TODO: Things that might be considered as Settings
        # - HighDpi Mode
        # - Logging Configurations
        # - A dumb mode, where the program just sends what is clicked without checking algorithms
        # - ATK, ATF ATT values
        # - Flashing capabilites

        self._master: ttk.Window = master
        self._main_frame: ttk.Frame = ttk.Frame(self)

        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._back_button: ttk.Button = ttk.Button(
            self._navigation_frame, text=const.ui.BACK_LABEL, style=ttk.DARK
        )
        self._title: ttk.Label = ttk.Label(self._navigation_frame, text="")
        self._save_button: ttk.Button = ttk.Button(
            self._navigation_frame, text=const.ui.SAVE_LABEL, style=ttk.SUCCESS
        )

        self._greeter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._flash_settings_button: ttk.Button = ttk.Button(
            self._greeter_frame, text=const.ui.FLASH_SETTINGS_LABEL, style=ttk.DARK
        )
        self._sonicamp_settings_button: ttk.Button = ttk.Button(
            self._greeter_frame, text=const.ui.SONICAMP_SETTINGS_LABEL, style=ttk.DARK
        )
        self._soniccontrol_settings_button: ttk.Button = ttk.Button(
            self._greeter_frame,
            text=const.ui.SONICCONTROL_SETTINGS_LABEL,
            style=ttk.DARK,
        )

        self._flash_settings_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._file_entry: ttk.Entry = ttk.Entry(self._flash_settings_frame)
        self._browse_files_button: ttk.Button = ttk.Button(
            self._flash_settings_frame, text=const.ui.SPECIFY_PATH_LABEL
        )
        self._submit_button: ttk.Button = ttk.Button(
            self._flash_settings_frame, text=const.ui.SUBMIT_LABEL
        )

        self._sonicamp_settings_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._config_entry: ttk.Combobox = ttk.Combobox(
            self._sonicamp_settings_frame, style=ttk.DARK
        )
        self._load_config_button: ttk.Button = ttk.Button(
            self._sonicamp_settings_frame, text=const.ui.LOAD_LABEL
        )
        self._atf1_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATF Frequency 1:"
        )
        self._atf2_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATF Frequency 2:"
        )
        self._atf3_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATF Frequency 3:"
        )
        self._atk1_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATK Coefficient 1:"
        )
        self._atk2_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATK Coefficient 2:"
        )
        self._atk3_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATK Coefficient 3:"
        )
        self._att1_frame: ATK_Frame = ATK_Frame(
            self._sonicamp_settings_frame, "ATT Temperature:"
        )
        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(const.images.SETTINGS_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return const.ui.SETTINGS_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._greeter_frame.pack(expand=True, fill=ttk.BOTH)
        self._sonicamp_settings_button.pack(expand=True)
        self._soniccontrol_settings_button.pack(expand=True)
        self._flash_settings_button.pack(expand=True)

    def publish(self) -> None:
        ...
