import asyncio
from typing import Callable

from ttkbootstrap.dialogs.dialogs import Messagebox
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.connection_builder import ConnectionBuilder
from soniccontrol.state_updater.logger import LogStorage, create_logger_for_connection
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.core.connection_window import DeviceWindowManager
from async_tkinter_loop import async_handler
import ttkbootstrap as ttk
from soniccontrol.utils import files


class CliConnectionWindow(UIComponent):
    def __init__(self):
        self._view = CliConnectionWindowView()
        super().__init__(None, self._view)
        self._device_window_manager = DeviceWindowManager(self._view)
        self._view.set_connect_button_command(self._attempt_connection)

    @async_handler
    async def _attempt_connection(self):
        process = await asyncio.create_subprocess_shell(
            str(files.files.CLI_MVC_MOCK),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        logger = create_logger_for_connection("simulation")

        logger.debug("Established serial connection")
        try:
            serial, commands = await ConnectionBuilder.build(
                reader=process.stdout,
                writer=process.stdin,
                logger=logger,
            )
            logger.debug("Build SonicAmp for device")
            sonicamp = await AmpBuilder().build_amp(ser=serial, commands=commands, logger=logger)
            await sonicamp.serial.connection_opened.wait()
        except ConnectionError as e:
            logger.error(e)
            Messagebox.show_error(e)
            return

        logger.info("Created device successfully, open device window")
        self._device_window_manager.open_device_window(sonicamp, logger)


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

    def set_connect_button_command(self, command: Callable[[], None]) -> None:
        self._connect_button.configure(command=command)
