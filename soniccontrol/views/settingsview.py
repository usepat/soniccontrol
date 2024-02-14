import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.utils.constants as const
from soniccontrol import utils
from soniccontrol.interfaces.layouts import Layout


class ATK_Frame(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, label: str, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._label: ttk.Label = ttk.Label(self, text=label)
        self._spinbox: ttk.Spinbox = ttk.Spinbox(self)

    def publish(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._label.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.E)
        self._spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.W)


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
        self._notebook: ttk.Notebook = ttk.Notebook(self._main_frame)

        self._flash_settings_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._flash_frame: ttk.Labelframe = ttk.Labelframe(
            self._flash_settings_frame, padding=(5, 0, 5, 5)
        )
        self._file_entry: ttk.Entry = ttk.Entry(self._flash_frame)
        self._browse_files_button: ttk.Button = ttk.Button(
            self._flash_frame, text=const.ui.SPECIFY_PATH_LABEL, style=ttk.DARK
        )
        self._submit_button: ttk.Button = ttk.Button(
            self._flash_frame, text=const.ui.SUBMIT_LABEL, style=ttk.DARK
        )

        self._sonicamp_settings_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._config_entry: ttk.Combobox = ttk.Combobox(
            self._sonicamp_settings_frame, style=ttk.DARK
        )
        self._save_config_button: ttk.Button = ttk.Button(
            self._sonicamp_settings_frame, text=const.ui.SAVE_LABEL, style=ttk.DARK
        )
        self._send_config_button: ttk.Button = ttk.Button(
            self._sonicamp_settings_frame, text=const.ui.SEND_LABEL, style=ttk.SUCCESS
        )
        self._parameters_frame: ScrolledFrame = ScrolledFrame(
            self._sonicamp_settings_frame, autohide=True
        )
        self._atf1_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATF Frequency 1:"
        )
        self._atf2_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATF Frequency 2:"
        )
        self._atf3_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATF Frequency 3:"
        )
        self._atk1_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATK Coefficient 1:"
        )
        self._atk2_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATK Coefficient 2:"
        )
        self._atk3_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATK Coefficient 3:"
        )
        self._att1_frame: ATK_Frame = ATK_Frame(
            self._parameters_frame, "ATT Temperature:"
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
        self._notebook.pack(expand=True, fill=ttk.BOTH)
        self._notebook.add(
            self._flash_settings_frame, text=const.ui.FLASH_SETTINGS_LABEL
        )
        self._notebook.add(
            self._sonicamp_settings_frame, text=const.ui.SONICAMP_SETTINGS_LABEL
        )

        self._flash_frame.pack(expand=True)
        self._flash_frame.columnconfigure(0, weight=1)
        self._flash_frame.columnconfigure(1, weight=0)
        self._flash_frame.rowconfigure(0, weight=0)
        self._flash_frame.rowconfigure(1, weight=0)
        self._file_entry.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._browse_files_button.grid(row=0, column=1, padx=5, pady=5)
        self._submit_button.grid(
            row=1, column=0, padx=5, pady=5, sticky=ttk.EW, columnspan=2
        )

        self._sonicamp_settings_frame.columnconfigure(0, weight=1)
        self._sonicamp_settings_frame.columnconfigure(1, weight=0)
        self._sonicamp_settings_frame.columnconfigure(2, weight=0)
        self._sonicamp_settings_frame.rowconfigure(1, weight=1)
        self._config_entry.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._save_config_button.grid(row=0, column=1, padx=5, pady=5)
        self._send_config_button.grid(row=0, column=2, padx=5, pady=5)
        self._parameters_frame.grid(
            row=1, column=0, padx=5, pady=5, columnspan=3, sticky=ttk.NSEW
        )
        self._parameters_frame.columnconfigure(0, weight=1)
        self._atf1_frame.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._atk1_frame.grid(row=1, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._atf2_frame.grid(row=2, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._atk2_frame.grid(row=3, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._atf3_frame.grid(row=4, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._atk3_frame.grid(row=5, column=0, padx=5, pady=5, sticky=ttk.EW)
        self._att1_frame.grid(row=6, column=0, padx=5, pady=5, sticky=ttk.EW)
        for child in self._parameters_frame.winfo_children():
            if hasattr(child, "publish"):
                child.publish()

    def publish(self) -> None:
        ...
