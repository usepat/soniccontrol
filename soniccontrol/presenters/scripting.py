from icecream import ic
from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.utils import constants
from soniccontrol.views.scriptingview import ScriptingView


class ScriptPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao script")
        self.bind_view()

    @property
    def view(self) -> ScriptingView:
        return self.master.views.scripting

    def bind_view(self):
        ic(self.view)
        self.view.start_button.configure(
            command=lambda: self.view.event_generate(
                constants.events.SCRIPT_START_EVENT
            )
        )
        self.view.bind(constants.events.SCRIPT_START_EVENT, self.view.on_script_start)
