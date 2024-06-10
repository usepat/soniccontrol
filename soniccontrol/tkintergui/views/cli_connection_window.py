import asyncio
from typing import Callable
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.sonicpackage.amp_data import Info, Status
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.connection_window import DeviceWindowManager
from async_tkinter_loop import async_handler
import ttkbootstrap as ttk
from soniccontrol.utils import files

class CliConnectionWindow(UIComponent):
    def __init__(self):
        self._view = CliConnectionWindowView()
        super().__init__(None, self._view)
        self._device_window_manager = DeviceWindowManager(self._view)
        self._view.set_connect_button_command(lambda: self._attempt_connection())

    @async_handler
    async def _attempt_connection(self):
        process = await asyncio.create_subprocess_shell(
            str(files.files.CLI_MVC_MOCK),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        serial = SerialCommunicator()
        await serial.connect(process.stdout, process.stdin)
        sonicamp = await AmpBuilder().build_amp(ser=serial, status=Status(), info=Info())
        await sonicamp.serial.connection_opened.wait()
        self._device_window_manager.open_device_window(sonicamp)


class CliConnectionWindowView(ttk.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._connect_button: ttk.Button = ttk.Button(
            self._main_frame,
            style=ttk.SUCCESS,
            text=ui_labels.CONNECT_LABEL,
        )

        self._main_frame.pack(fill=ttk.BOTH, expand=True)
        self._connect_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)


    def set_connect_button_command(self, command: Callable[[None], None]) -> None:
        self._connect_button.configure(command=command)
