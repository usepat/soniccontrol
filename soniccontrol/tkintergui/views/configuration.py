
from typing import Callable, List, Iterable, Dict, Optional
import attrs
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
import json
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
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


@attrs.define()
class Config:
    transducers: List[TransducerConfig] = attrs.field()
    hexmode: bool = attrs.field()
    devmode: bool = attrs.field()


class Configuration(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp):
        self._count_atk_atf = 4
        self._config = Config()
        self._view = ConfigurationView(parent.view, self._count_atk_atf)
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

        self.view.devmode = self._config.devmode
        self.view.hexmode = self._config.hexmode
        self.view.set_transducer_config_menu_items(map(lambda config: config.name, self._config.transducers))
        self.current_transducer_config = 0 if len(self._config.transducers) > 0 else None

    def _save_config(self):
        self._config.devmode = self.view.devmode
        self._config.hexmode = self.view.hexmode
    
        transducer_config = TransducerConfig(name=self.view.transducer_config_name, atconfigs=self.view.atconfigs)
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
        return True

    def _on_transducer_config_changed(self):
        if self.current_transducer_config is None:
            self._add_transducer_config_template()
        else:
            current_config = self._config.transducers[self.current_transducer_config]
            self.view.selected_transducer_config = current_config.name
            self.view.transducer_config_name = current_config.name
            self.view.atconfigs = current_config.ats

    def _add_transducer_config_template(self):
        self.view.atconfigs = [ATConfig()] * self._count_atk_atf
        self.view.transducer_config_name = "no name"
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
        for i, atconfig in enumerate(self.view.atconfigs):
            await self._device.set_atf(i, atconfig.atf)
            await self._device.set_atk(i, atconfig.atk)
            await self._device.set_att(i, atconfig.att)
            await self._device.set_aton(i, atconfig.aton)

    def _flash(self):
        pass #TODO


class ConfigurationView(TabView):
    def __init__(self, master: ttk.Frame, count_atk_atf: int, *args, **kwargs):
        self._count_atk_atf = count_atk_atf
        super().__init__(*args, **kwargs)

    def set_save_config_command(self, command: Callable[[None], None]) -> None:
        pass

    def set_load_config_command(self, command: Callable[[None], None]) -> None:
        pass

    def set_transducer_config_changed_command(self, command: Callable[[None], None]) -> None:
        pass

    def set_add_transducer_config_command(self, command: Callable[[None], None]) -> None:
        pass

    def set_submit_transducer_config_command(self, command: Callable[[None], None]) -> None:
        pass

    def set_flash_command(self, command: Callable[[None], None]) -> None:
        pass

    @property 
    def atconfigs(self) -> List[ATConfig]:
        pass

    @atconfigs.setter
    def atconfigs(self, values: Iterable[ATConfig]) -> None:
        pass

    @property
    def hexmode(self) -> bool:
        pass

    @hexmode.setter
    def hexmode(self, value: bool) -> None:
        pass

    @property
    def devmode(self) -> bool:
        pass

    @devmode.setter
    def devmode(self, value: bool) -> None:
        pass

    @property
    def selected_transducer_config(self) -> str:
        pass

    @selected_transducer_config.setter
    def selected_transducer_config(self, value: str) -> None:
        pass

    def set_transducer_config_menu_items(self, items: Iterable[str]) -> None:
        pass
    
    @property
    def transducer_config_name(self) -> str:
        pass

    @transducer_config_name.setter
    def transducer_config_name(self, value: str) -> None:
        pass
