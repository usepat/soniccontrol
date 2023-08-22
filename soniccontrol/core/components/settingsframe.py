import logging
from typing import Iterable
import ttkbootstrap as ttk
import PIL
from PIL.ImageTk import PhotoImage
from soniccontrol.interfaces import RootChild, Layout
from soniccontrol.sonicamp import Command

import soniccontrol.constants as const

logger = logging.getLogger(__name__)


class SettingsFrame(RootChild):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)

        self.restart_image: PhotoImage = const.Images.get_image(
            const.Images.REFRESH_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )

        self.navigation_bar: ttk.Frame = ttk.Frame(self)
        self.load_config_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Load config.json",
            bootstyle=ttk.INFO,
            image=self.restart_image,
            compound=ttk.LEFT,
            command=self.load_config_json,
        )

        self.mainframe: ttk.Frame = ttk.Frame(self)
        self.flash_frame: ttk.Labelframe = ttk.Labelframe(
            self.mainframe, text="Update your device"
        )
        self.file_entry = ttk.Button(
            self.flash_frame,
            text="Specify path for Firmware file",
            style=ttk.DARK,
            command=self.get_flash_file,
        )
        self.upload_button = ttk.Button(
            self.flash_frame,
            style="dark.TButton",
            width=23,
            text="Update device",
            state=ttk.DISABLED,
            command=self.upload_file,
        )

        self.atf_configuration_frame: ttk.Frame = ttk.Labelframe(
            self.mainframe, text="Configure ATF frequencies..."
        )

        self.atf1_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf1_label: ttk.Label = ttk.Label(self.atf1_frame, text="ATF1 frequency:")
        self.atf1_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf1_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf1,
        )

        self.atk1_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atk1_label: ttk.Label = ttk.Label(
            self.atk1_frame, text="ATK1 coefficient:"
        )
        self.atk1_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atk1_frame,
            from_=(-20_000_000),
            to=20_000_000,
            increment=100,
            textvariable=self.root._atk1,
        )

        self.atf2_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf2_label: ttk.Label = ttk.Label(self.atf2_frame, text="ATF2 frequency:")
        self.atf2_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf2_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf2,
        )

        self.atk2_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atk2_label: ttk.Label = ttk.Label(
            self.atk2_frame, text="ATK2 coefficient:"
        )
        self.atk2_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atk2_frame,
            from_=(-20_000_000),
            to=20_000_000,
            increment=100,
            textvariable=self.root._atk2,
        )

        self.atf3_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf3_label: ttk.Label = ttk.Label(self.atf3_frame, text="ATF3 frequency:")
        self.atf3_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf3_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf3,
        )

        self.atk3_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atk3_label: ttk.Label = ttk.Label(
            self.atk3_frame, text="ATK3 coefficient:"
        )
        self.atk3_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atk3_frame,
            from_=(-20_000_000),
            to=20_000_000,
            increment=100,
            textvariable=self.root._atk3,
        )

        self.att1_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.att1_label: ttk.Label = ttk.Label(
            self.att1_frame, text="ATT1 coefficient:"
        )
        self.att1_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.att1_frame,
            from_=(-273.15),
            to=2_000,
            increment=10,
            textvariable=self.root._att1,
        )

        self.submit_button: ttk.Button = ttk.Button(
            self.atf_configuration_frame,
            text="Submit and save configuration",
            bootstyle=ttk.DARK,
            command=self.submit_atf_configuration,
        )
        self.bind_events()
        self.publish()

    def on_connect(self, *args, **kwargs) -> None:
        pass

    def publish(self) -> None:
        self.navigation_bar.pack(fill=ttk.X)
        self.load_config_button.pack(side=ttk.LEFT, padx=5, pady=5)
        
        self.mainframe.pack()
        self.flash_frame.pack(padx=5, pady=10, fill=ttk.X)
        self.file_entry.pack(fill=ttk.X, padx=5, pady=5)
        self.upload_button.pack(fill=ttk.X, padx=5, pady=5)

        self.atf_configuration_frame.pack(padx=5, pady=5)
        self.atf1_frame.pack(padx=5, pady=10)
        self.atf1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atk1_frame.pack(padx=5, pady=5)
        self.atk1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atf2_frame.pack(padx=5, pady=5)
        self.atf2_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf2_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atk2_frame.pack(padx=5, pady=5)
        self.atk2_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk2_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atf3_frame.pack(padx=5, pady=5)
        self.atf3_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf3_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atk3_frame.pack(padx=5, pady=5)
        self.atk3_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk3_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.att1_frame.pack(padx=5, pady=5)
        self.att1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.att1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.submit_button.pack(padx=5, pady=10)

    def submit_atf_configuration(self) -> None:
        self.save_config()

        self.root.sonicamp.add_job(Command(message=f"!atf1={self.root._atf1.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk1={self.root._atk1.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!atf2={self.root._atf2.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk2={self.root._atk2.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!atf3={self.root._atf3.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk3={self.root._atk3.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!att1={self.root._att1.get()}"), 0)

    def upload_file(self) -> None:
        pass

    def get_flash_file(self) -> None:
        pass

    def load_config_json(self) -> None:
        pass

    def load_atf_config(self) -> None:
        pass

    def save_atf_config(self) -> None:
        pass
