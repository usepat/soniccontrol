
import asyncio
from pathlib import Path
from typing import Callable, List, Iterable, Optional
import attrs
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame
import json
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.sonicpackage.script.legacy_scripting import LegacyScriptingFacade
from soniccontrol.sonicpackage.script.scripting_facade import ScriptingFacade
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.file_browse_button import FileBrowseButtonView
from soniccontrol.utils import files
from async_tkinter_loop import async_handler


@attrs.define()
class ATConfig:
    atk: int = attrs.field(default=0)
    atf: int = attrs.field(default=0)
    att: int = attrs.field(default=0)
    aton: int = attrs.field(default=0)

@attrs.define()
class TransducerConfig():
    name: str = attrs.field()
    ats: List[ATConfig] = attrs.field()
    init_script_path: Optional[Path] = attrs.field(default=None)

@attrs.define()
class Config:
    transducers: List[TransducerConfig] = attrs.field(default=[])

class ATConfigFrame(UIComponent):
    def __init__(self, parent: UIComponent, view_parent: View, index: int):
        self._index = index
        self._view = ATConfigFrameView(view_parent, index)
        super().__init__(parent, self._view)

    @property
    def value(self) -> ATConfig:
        return ATConfig(
            atk = self._view.atk,
            atf = self._view.atf,
            att = self._view.att,
            aton = self._view.aton
        )
    
    @value.setter
    def value(self, config: ATConfig) -> None:
        self._view.atf = config.atf
        self._view.atk = config.atk
        self._view.att = config.att
        self._view.aton = config.aton


class ATConfigFrameView(View):
    def __init__(self, master: ttk.Frame, index: int, *args, **kwargs):
        self._index = index
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._atf_var = ttk.StringVar()
        self._atk_var = ttk.StringVar()
        self._att_var = ttk.StringVar()
        self._aton_var = ttk.StringVar()
    
        self._atf_label = ttk.Label(self, text=f"ATF {self._index}")
        self._atk_label = ttk.Label(self, text=f"ATK {self._index}")
        self._att_label = ttk.Label(self, text=f"ATT {self._index}")
        self._aton_label = ttk.Label(self, text=f"ATON {self._index}")

        self._atf_spinbox = ttk.Spinbox(self, textvariable=self._atf_var)
        self._atk_spinbox = ttk.Spinbox(self, textvariable=self._atk_var)
        self._att_spinbox = ttk.Spinbox(self, textvariable=self._att_var)
        self._aton_spinbox = ttk.Spinbox(self, textvariable=self._aton_var)

    def _initialize_publish(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self._atf_label.grid(row=0, column=0, padx=10, pady=10, sticky=ttk.E)
        self._atf_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky=ttk.W)

        self._atk_label.grid(row=1, column=0, padx=10, pady=10, sticky=ttk.E)
        self._atk_spinbox.grid(row=1, column=1, padx=10, pady=10, sticky=ttk.W)

        self._att_label.grid(row=2, column=0, padx=10, pady=10, sticky=ttk.E)
        self._att_spinbox.grid(row=2, column=1, padx=10, pady=10, sticky=ttk.W)

        self._aton_label.grid(row=3, column=0, padx=10, pady=10, sticky=ttk.E)
        self._aton_spinbox.grid(row=3, column=1, padx=10, pady=10, sticky=ttk.W)

    # Properties for atf
    @property
    def atf(self):
        return self._atf_var.get()

    @atf.setter
    def atf(self, value):
        self._atf_var.set(value)

    # Properties for atk
    @property
    def atk(self):
        return self._atk_var.get()

    @atk.setter
    def atk(self, value):
        self._atk_var.set(value)

    # Properties for att
    @property
    def att(self):
        return self._att_var.get()

    @att.setter
    def att(self, value):
        self._att_var.set(value)

    # Properties for aton
    @property
    def aton(self):
        return self._aton_var.get()

    @aton.setter
    def aton(self, value):
        self._aton_var.set(value)
    

class Configuration(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp):
        self._count_atk_atf = 4
        self._config = Config()
        self._view = ConfigurationView(parent.view, self, self._count_atk_atf)
        self._current_transducer_config: Optional[int] = None
        self._device = device
        super().__init__(parent, self._view)

    @property
    def current_transducer_config(self) -> Optional[int]:
        return self._current_transducer_config

    @current_transducer_config.setter
    def current_transducer_config(self, value: Optional[int]) -> None:
        if value != self._current_transducer_config:
            self._current_transducer_config = value
            self._on_transducer_config_changed()

    def _load_config(self):
        with open(files.CONFIG_JSON, "r") as file:
            self._config = json.load(file)

        self.view.set_transducer_config_menu_items(map(lambda config: config.name, self._config.transducers))
        self.current_transducer_config = 0 if len(self._config.transducers) > 0 else None

    def _save_config(self):
        init_script_path: str = self.view.init_script_path # TODO rework this shit, so that a browse files component is used instead
        transducer_config = TransducerConfig(
            name=self.view.transducer_config_name, 
            atconfigs=self.view.atconfigs, 
            init_script_path= None if init_script_path.isspace() or len(init_script_path) == 0 else Path(init_script_path)
        )
        if not self._validate_transducer_config_data(transducer_config):
            return

        if self.current_transducer_config is None:
            self._config.transducers.append(transducer_config)
            self._current_transducer_config = len(self._config.transducers) - 1
            self.view.set_transducer_config_menu_items(map(lambda config: config.name, self._config.transducers))
        else:
            self._config.transducers[self.current_transducer_config] = transducer_config

        with open(files.CONFIG_JSON, "w") as file:
            json.dump(self._config, file)

    def _validate_transducer_config_data(self, transducer_config: TransducerConfig) -> bool:            
        if self.current_transducer_config is not None and any(lambda tconfig: tconfig.name == transducer_config.name, self._config.transducers):
            Messagebox.show_error("config with the same name already exists")
            return False
        if transducer_config.init_script_path is not None and not transducer_config.init_script_path.exists():
            Messagebox.show_error("there exists no init script with the specified path")
            return False
        return True

    def _on_transducer_config_changed(self):
        if self.current_transducer_config is None:
            self._add_transducer_config_template()
        else:
            current_config = self._config.transducers[self.current_transducer_config]
            self.view.selected_transducer_config = current_config.name
            self.view.transducer_config_name = current_config.name
            self.view.atconfigs = current_config.ats
            self.view.init_script_path = "" if current_config.init_script_path is None else current_config.init_script_path.as_posix()

    def _add_transducer_config_template(self):
        self.view.atconfigs = [ATConfig()] * self._count_atk_atf
        self.view.transducer_config_name = "no name"
        self.view.init_script_path = ""
        self.current_transducer_config = None

    def _delete_transducer_config(self):
        if self.current_transducer_config is None:
            return

        self._config.transducers.pop(self.current_transducer_config)
        with open(files.CONFIG_JSON, "w") as file:
            json.dump(self._config, file)

        self.view.set_transducer_config_menu_items(map(lambda config: config.name, self._config.transducers))
        self._add_transducer_config_template()

    @async_handler
    async def _submit_transducer_config(self):
        # TODO: start load animation

        for i, atconfig in enumerate(self.view.atconfigs):
            await self._device.set_atf(i, atconfig.atf)
            await self._device.set_atk(i, atconfig.atk)
            await self._device.set_att(i, atconfig.att)
            await self._device.set_aton(i, atconfig.aton)

        asyncio.create_task(self._interpreter_engine())

    async def _interpreter_engine(self):
        script_file_path = self._config.transducers[self._current_transducer_config].init_script_path
        with open(script_file_path, "r") as f:
            script = f.read()
        scripting: ScriptingFacade = LegacyScriptingFacade(self._device)
        interpreter = scripting.parse_script(script)

        try:
            while next(interpreter, None):
                pass
        except asyncio.CancelledError:
            return
        except Exception as e:
            Messagebox.show_error(e)
            return
        finally:
            pass # TODO: end load animation


class ConfigurationView(TabView):
    def __init__(self, master: ttk.Frame, presenter: UIComponent, count_atk_atf: int, *args, **kwargs):
        self._presenter = presenter
        self._count_atk_atf = count_atk_atf
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.SETTINGS_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SETTINGS_LABEL

    def _initialize_children(self) -> None:
        self._config_frame: ttk.Frame = ttk.Frame(self)
        self._add_config_button: ttk.Button = ttk.Button(
            self._config_frame,
            text=ui_labels.NEW_LABEL,
            style=ttk.DARK,
            # image=utils.ImageLoader.load_image(
            #     images.PLUS_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            # ),
        )
        self._selected_config: ttk.StringVar = ttk.StringVar()
        self._config_entry: ttk.Combobox = ttk.Combobox(
            self._config_frame, textvariable=self._selected_config, style=ttk.DARK
        )
        self._config_entry["state"] = "readonly" # prevent typing a value
        self._save_config_button: ttk.Button = ttk.Button(
            self._config_frame, text=ui_labels.SAVE_LABEL, style=ttk.DARK
        )
        self._submit_config_button: ttk.Button = ttk.Button(
            self._config_frame, text=ui_labels.SEND_LABEL, style=ttk.SUCCESS
        )

        self._transducer_config_frame: ttk.Frame = ttk.Frame(
            self._config_frame
        )
        self._config_name: ttk.StringVar = ttk.StringVar()
        self._config_name_textbox: ttk.Entry = ttk.Entry(
            self._transducer_config_frame, textvariable=self._config_name
        )
        self._atconfigs_frame: ScrolledFrame = ScrolledFrame(self._transducer_config_frame)
        self._atconfig_frames: List[ATConfigFrame] = []
        for i in range(0, self._count_atk_atf):
            self._atconfig_frames.append(ATConfigFrame(self._presenter, self._atconfigs_frame, i))
        self._browse_script_init_button: FileBrowseButtonView = FileBrowseButtonView(
            self._transducer_config_frame, text=ui_labels.SPECIFY_PATH_LABEL, style=ttk.DARK
        )

    def _initialize_publish(self) -> None:
        self._config_frame.pack(expand=True, fill=ttk.BOTH)
        self._config_frame.columnconfigure(0, weight=sizes.DONT_EXPAND)
        self._config_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._config_frame.columnconfigure(2, weight=sizes.DONT_EXPAND)
        self._config_frame.columnconfigure(3, weight=sizes.DONT_EXPAND)
        self._config_frame.rowconfigure(0, weight=sizes.DONT_EXPAND)
        self._config_frame.rowconfigure(1, weight=sizes.EXPAND)
        self._add_config_button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._config_entry.grid(
            row=0,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._save_config_button.grid(
            row=0,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._submit_config_button.grid(
            row=0,
            column=3,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )

        self._transducer_config_frame.grid(row=1, column=0, columnspan=4, sticky=ttk.NSEW)
        self._transducer_config_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._transducer_config_frame.rowconfigure(0, weight=sizes.DONT_EXPAND)
        self._transducer_config_frame.rowconfigure(1, weight=sizes.EXPAND)
        self._transducer_config_frame.rowconfigure(2, weight=sizes.DONT_EXPAND)
        self._config_name_textbox.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._atconfigs_frame.grid(
            row=1,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.NSEW,
        )
        for i, atconfig_frame in enumerate(self._atconfig_frames):
            atconfig_frame.view.grid(row=i, column=0, padx=sizes.MEDIUM_PADDING, pady=sizes.MEDIUM_PADDING, sticky=ttk.EW)

        self._browse_script_init_button.grid(
            row=2,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )

    def set_save_config_command(self, command: Callable[[None], None]) -> None:
        self._save_config_button.configure(command=command)

    def set_transducer_config_changed_command(self, command: Callable[[None], None]) -> None:
        self._config_entry.bind("<<ComboboxSelected>>", lambda _: command())

    def set_add_transducer_config_command(self, command: Callable[[None], None]) -> None:
        self._add_config_button.configure(command=command)

    def set_submit_transducer_config_command(self, command: Callable[[None], None]) -> None:
        self._submit_config_button.configure(command=command)

    @property 
    def atconfigs(self) -> List[ATConfig]:
        return list(map(lambda x: x.value, self._atconfig_frames))

    @atconfigs.setter
    def atconfigs(self, values: Iterable[ATConfig]) -> None:
        for i, atconfig in enumerate(values):
            self._atconfig_frames[i].value = atconfig

    @property
    def init_script_path(self) -> Optional[Path]:
        return self._browse_script_init_button.path

    @init_script_path.setter
    def init_script_path(self, value: Optional[Path]) -> None:
        self._browse_script_init_button.path = value

    @property
    def selected_transducer_config(self) -> str:
        return self._selected_config.get()

    @selected_transducer_config.setter
    def selected_transducer_config(self, value: str) -> None:
        self._selected_config.set(value)

    def set_transducer_config_menu_items(self, items: Iterable[str]) -> None:
        self._config_entry["values"] = items
    
    @property
    def transducer_config_name(self) -> str:
        return self._config_name.get()

    @transducer_config_name.setter
    def transducer_config_name(self, value: str) -> None:
        self._config_name.set(value)
