import time
from typing import Any

import ttkbootstrap as ttk
from icecream import ic
from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.utils import constants
from soniccontrol.views.settingsview import SettingsView


class SettingsPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao settings")
        self.bind_view()

    @property
    def view(self) -> SettingsView:
        return self.master.views.settings

    def bind_view(self) -> None:
        self.view._config_entry.configure(
            textvariable=self.master.atf_vars.atf_config_name
        )
        self.view._new_config_button.configure(command=self.create_new_config)
        self.view._save_config_button.configure(
            command=lambda: self.master.event_generate(constants.events.SAVE_CONFIG)
        )
        self.view._send_config_button.configure(command=self.submit_config)
        self.view._atf1_frame.bind_variable(self.master.atf_vars.atf1)
        self.view._atk1_frame.bind_variable(self.master.atf_vars.atk1)
        self.view._atf2_frame.bind_variable(self.master.atf_vars.atf2)
        self.view._atk2_frame.bind_variable(self.master.atf_vars.atk2)
        self.view._atf3_frame.bind_variable(self.master.atf_vars.atf3)
        self.view._atk3_frame.bind_variable(self.master.atf_vars.atk3)
        self.view._att1_frame.bind_variable(self.master.atf_vars.att1)
        self.view._progress_bar.configure(
            variable=self.master.atf_vars.submitting_progress
        )

    def submit_config(self) -> None:
        ic("Sending config to device...")

    def set_config(self, config: dict[str, Any]) -> None:
        self.master.atf_vars.atf1.set(config["atf1"])
        self.master.atf_vars.atk1.set(config["atk1"])
        self.master.atf_vars.atf2.set(config["atf2"])
        self.master.atf_vars.atk2.set(config["atk2"])
        self.master.atf_vars.atf3.set(config["atf3"])
        self.master.atf_vars.atk3.set(config["atk3"])
        self.view._commandset_frame.delete(1.0, ttk.END)
        self.view._commandset_frame.insert(ttk.INSERT, config["commandset"])

    def create_new_config(self) -> None:
        self.master.atf_vars.atf_config_name.set("")
        self.master.atf_vars.atf1.set(0)
        self.master.atf_vars.atk1.set(0)
        self.master.atf_vars.atf2.set(0)
        self.master.atf_vars.atk2.set(0)
        self.master.atf_vars.atf3.set(0)
        self.master.atf_vars.atk3.set(0)
