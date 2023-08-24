import logging
from typing import Iterable, List, Dict, Any, Optional
import ttkbootstrap as ttk
from tkinter import filedialog
from ttkbootstrap.dialogs import Messagebox
import PIL
from PIL.ImageTk import PhotoImage
from dataclasses import dataclass, field, asdict
from soniccontrol.interfaces import RootChild, Layout, Connectable
from soniccontrol.sonicamp import Command
from soniccontrol.interfaces.tkinter_vars import RootStringVar

import platform
import subprocess
import sys
import json
import time
import threading
import pathlib

import soniccontrol.constants as const

logger = logging.getLogger(__name__)


class SettingsFrame(RootChild, Connectable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)

        self.restart_image: PhotoImage = const.Images.get_image(
            const.Images.REFRESH_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )

        self.validation_ended: threading.Event = threading.Event()
        self.validation_result: threading.Event = threading.Event()

        self.file_entry_textvar: RootStringVar = RootStringVar(
            value="Specify and validate Firmwarefile", master=self
        )
        self.config_json_file: pathlib.Path = pathlib.Path("config.json")

        self.navigation_bar: ttk.Frame = ttk.Frame(self)
        self.load_config_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Refresh config.json",
            bootstyle=ttk.INFO,
            image=self.restart_image,
            compound=ttk.LEFT,
            command=self.load_config_json,
        )

        self.mainframe: ttk.Frame = ttk.Frame(self)

        self.flash_frame_container: ttk.Frame = ttk.Frame(self.mainframe)
        self.flash_frame: ttk.Labelframe = ttk.Labelframe(
            self.flash_frame_container, text="Update your device"
        )
        self.file_entry = ttk.Button(
            self.flash_frame,
            textvariable=self.file_entry_textvar,
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

        self.atf_configuration_frame_container: ttk.Frame = ttk.Frame(self.mainframe)
        self.atf_configuration_frame: ttk.Frame = ttk.Labelframe(
            self.atf_configuration_frame_container, text="Configure ATF frequencies..."
        )

        self.config_entry_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.config_entry: ttk.Combobox = ttk.Combobox(
            self.config_entry_frame,
            textvariable=self.root.atf_configuration_name,
            bootstyle=ttk.DARK,
        )
        self.load_atf_config_button: ttk.Button = ttk.Button(
            self.config_entry_frame,
            text="Load config...",
            bootstyle=ttk.DARK,
            command=self.load_atf_config,
        )

        self.at1_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf1_frame: ttk.Frame = ttk.Frame(self.at1_frame)
        self.atf1_label: ttk.Label = ttk.Label(self.atf1_frame, text="ATF1 frequency:")
        self.atf1_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf1_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf1,
        )

        self.atk1_frame: ttk.Frame = ttk.Frame(self.at1_frame)
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

        self.at2_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf2_frame: ttk.Frame = ttk.Frame(self.at2_frame)
        self.atf2_label: ttk.Label = ttk.Label(self.atf2_frame, text="ATF2 frequency:")
        self.atf2_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf2_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf2,
        )

        self.atk2_frame: ttk.Frame = ttk.Frame(self.at2_frame)
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

        self.at3_frame: ttk.Frame = ttk.Frame(self.atf_configuration_frame)
        self.atf3_frame: ttk.Frame = ttk.Frame(self.at3_frame)
        self.atf3_label: ttk.Label = ttk.Label(self.atf3_frame, text="ATF3 frequency:")
        self.atf3_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.atf3_frame,
            from_=0,
            to=20_000_000,
            increment=1000,
            textvariable=self.root._atf3,
        )

        self.atk3_frame: ttk.Frame = ttk.Frame(self.at3_frame)
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
            self.att1_frame, text="ATT1 temperature:"
        )
        self.att1_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.att1_frame,
            from_=(-273.15),
            to=2_000,
            increment=10,
            textvariable=self.root._att1,
        )

        self.atf_config_action_frame: ttk.Frame = ttk.Frame(
            self.atf_configuration_frame
        )
        self.request_current_config_button: ttk.Button = ttk.Button(
            self.atf_config_action_frame,
            text="Request current config",
            bootstyle=ttk.DARK,
            command=self.request_current_config,
        )
        self.submit_button: ttk.Button = ttk.Button(
            self.atf_config_action_frame,
            text="Submit and save",
            bootstyle=ttk.SUCCESS,
            command=self.submit_atf_configuration,
        )
        self.bind_events()

    def on_connect(self, *args, **kwargs) -> None:
        self.publish()
        self.load_config_json()
        self.request_current_config()

    def publish(self) -> None:
        self.navigation_bar.pack(fill=ttk.X)
        self.load_config_button.pack(side=ttk.LEFT, padx=5, pady=5)

        self.mainframe.pack()

        self.flash_frame_container.pack(fill=ttk.X)
        # self.flash_frame.pack(padx=5, pady=10, fill=ttk.X)
        self.file_entry.pack(fill=ttk.X, padx=5, pady=5)
        self.upload_button.pack(fill=ttk.X, padx=5, pady=5)

        self.atf_configuration_frame_container.pack(fill=ttk.X)
        self.atf_configuration_frame.pack(padx=5, pady=10)
        self.config_entry_frame.pack()
        self.config_entry.pack(side=ttk.LEFT, padx=5, pady=5, fill=ttk.X)
        self.load_atf_config_button.pack(side=ttk.LEFT, padx=5, pady=5, fill=ttk.X)

        self.at1_frame.pack(padx=5, pady=5)
        self.atf1_frame.pack(padx=5, pady=3)
        self.atf1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk1_frame.pack(padx=5, pady=5)
        self.atk1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.at2_frame.pack(padx=5, pady=5)
        self.atf2_frame.pack(padx=5, pady=3)
        self.atf2_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf2_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk2_frame.pack(padx=5, pady=5)
        self.atk2_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk2_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.at3_frame.pack(padx=5, pady=5)
        self.atf3_frame.pack(padx=5, pady=3)
        self.atf3_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atf3_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk3_frame.pack(padx=5, pady=5)
        self.atk3_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.atk3_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.att1_frame.pack(padx=5, pady=5)
        self.att1_label.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)
        self.att1_spinbox.pack(side=ttk.LEFT, fill=ttk.BOTH, padx=5, pady=5)

        self.atf_config_action_frame.pack(padx=5, pady=5)
        self.request_current_config_button.pack(side=ttk.LEFT, padx=5, pady=5)
        self.submit_button.pack(side=ttk.LEFT, padx=5, pady=5)

    def submit_atf_configuration(self) -> None:
        self.save_atf_config()

        self.root.sonicamp.add_job(Command(message=f"!atf1={self.root._atf1.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk1={self.root._atk1.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!atf2={self.root._atf2.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk2={self.root._atk2.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!atf3={self.root._atf3.get()}"), 0)
        self.root.sonicamp.add_job(Command(message=f"!atk3={self.root._atk3.get()}"), 0)

        self.root.sonicamp.add_job(Command(message=f"!att1={self.root._att1.get()}"), 0)

    def request_current_config(self) -> None:
        self.root.sonicamp.add_job(Command(message=f"?atf1"), 0)
        self.root.sonicamp.add_job(Command(message=f"?atf2"), 0)
        self.root.sonicamp.add_job(Command(message=f"?atf3"), 0)
        self.root.sonicamp.add_job(Command(message=f"?att1"), 0)

    def upload_file(self) -> None:
        answer: str = Messagebox.okcancel(
            message="You are about to update your device with a new Firmware. Please make sure, that the device stays on during the update and remains connected firmwly to the computer",
            title="Update warning",
            alert=True,
        )
        if answer == "cancel":
            return
        self.event_generate(const.Events.FIRMWARE_FLASH)

    def get_flash_file(self) -> None:
        self.file_entry.configure(bootstyle=ttk.DARK)
        self.upload_button.configure(state=ttk.DISABLED)

        self.root.firmware_flash_file = pathlib.Path(
            filedialog.askopenfilename(
                defaultextension=".hex",
                filetypes=(("HEX File", "*.hex"),),
            )
        )
        if not self.root.firmware_flash_file.exists():
            Messagebox.show_error("File does not exist", "Invalid File")
            return

        logger.debug("Validation succeeded!")
        self.file_entry.configure(bootstyle=ttk.SUCCESS)
        self.file_entry_textvar.set("File specified and validated")
        self.upload_button.configure(state=ttk.NORMAL)

    def load_config_json(self) -> None:
        if not self.config_json_file.exists():
            self.create_template()
        with open(self.config_json_file, "r") as file:
            file_content: str = file.read()
            logger.debug(f"File content: {file_content}")
            if len(file_content) == 0:
                self.create_template()

        with open(self.config_json_file, "r") as file:
            config_dict: Dict[str, Any] = json.load(file)
            logger.debug(f"Dictionary: {config_dict}")
            if not config_dict:
                self.create_template()

        with open(self.config_json_file, "r") as file:
            config_dict: Dict[str, Any] = json.load(file)
            self.sc_configuration = SonicControlConfig(**config_dict)
            logger.debug(f"Dataclass: {self.sc_configuration}")

            if self.sc_configuration.hexflash:
                self.flash_frame.pack(padx=5, pady=10, fill=ttk.X)
            if self.sc_configuration.devmode:
                # activate dev mode...
                pass
            if self.sc_configuration.transducer_configs:
                self.config_entry.configure(
                    values=[
                        tc.name
                        for tc in self.sc_configuration.transducer_configs.values()
                    ]
                )

    def create_template(self) -> str:
        action_answer: Optional[str] = Messagebox.okcancel(
            message='No "config.json" File found. Hence, a template will be created.',
            title="File not found",
        )
        if action_answer == "cancel":
            return
        self.config_json_file: pathlib.Path = pathlib.Path("config.json")
        self.sc_configuration = SonicControlConfig()
        with open(self.config_json_file, "w+") as file:
            logger.debug(asdict(self.sc_configuration))
            file.write(json.dumps(asdict(self.sc_configuration), indent=4))
            return file.read()

    def load_atf_config(self) -> None:
        if self.sc_configuration is None:
            self.load_config_json()

        logger.debug(f"Loading {self.root.atf_configuration_name.get()}")
        transducer_config: TransducerConfig = (
            self.sc_configuration.transducer_configs.get(
                self.root.atf_configuration_name.get(), "Template Config"
            )
        )
        logger.debug(f"Transducer config: {transducer_config}")
        self.root._atf1.set(transducer_config.atf1)
        self.root._atk1.set(transducer_config.atk1)

        self.root._atf2.set(transducer_config.atf2)
        self.root._atk2.set(transducer_config.atk2)

        self.root._atf3.set(transducer_config.atf3)
        self.root._atk3.set(transducer_config.atk3)

        self.root._att1.set(transducer_config.att1)

    def save_atf_config(self) -> None:
        with open(self.config_json_file, "w") as file:
            name: str = self.root.atf_configuration_name.get()

            if self.sc_configuration.transducer_configs.get(name) is not None:
                answer: str = Messagebox.show_question(
                    f"You are about to overwrite configurations for the transducer config named '{name}'. Are you really sure to overwrite the configuration?",
                    "Overwrite Warning",
                )
                if answer == "no":
                    return

            transducer_config: TransducerConfig = TransducerConfig(
                name=name,
                atf1=self.root._atf1.get(),
                atk1=self.root._atk1.get(),
                atf2=self.root._atf2.get(),
                atk2=self.root._atk2.get(),
                atf3=self.root._atf3.get(),
                atk3=self.root._atk3.get(),
                att1=self.root._att1.get(),
            )
            self.sc_configuration.transducer_configs[name] = transducer_config
            file.write(json.dumps(asdict(self.sc_configuration)))


@dataclass
class TransducerConfig:
    name: str = field(default="Template Config")
    atf1: int = field(default=0)
    atk1: float = field(default=0.0)
    atf2: int = field(default=0)
    atk2: float = field(default=0.0)
    atf3: int = field(default=0)
    atk3: float = field(default=0.0)
    att1: float = field(default=0.0)


@dataclass
class SonicControlConfig:
    hexflash: bool = field(default=False)
    devmode: bool = field(default=False)
    transducer_configs: Dict[str, TransducerConfig] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.transducer_configs:
            transducer: TransducerConfig = TransducerConfig()
            self.transducer_configs[transducer.name] = transducer
        else:
            self.transducer_configs = {
                name: TransducerConfig(
                    name, **{k: v for k, v in tc.items() if k != "name"}
                )
                if isinstance(tc, dict)
                else tc
                for name, tc in self.transducer_configs.items()
            }
