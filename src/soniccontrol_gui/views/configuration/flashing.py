
import asyncio
from typing import Final, Callable
from soniccontrol_gui.state_fetching.updater import Updater
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import TabView
from sonicpackage.communication.serial_communicator import LegacySerialCommunicator, SerialCommunicator
from sonicpackage.flashing.firmware_flasher import LegacyFirmwareFlasher, NewFirmwareFlasher
from sonicpackage.sonicamp_ import SonicAmp

from async_tkinter_loop import async_handler

import ttkbootstrap as ttk

from soniccontrol_gui.constants import sizes, ui_labels
from sonicpackage.events import PropertyChangeEvent
from soniccontrol_gui.views.core.app_state import AppState
from soniccontrol_gui.resources import images
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.widgets.file_browse_button import FileBrowseButtonView


class Flashing(UIComponent):
    RECONNECT_EVENT = "Reconnect"
    def __init__(self, parent: UIComponent, device: SonicAmp, app_state: AppState, updater: Updater):
        if isinstance(device._serial, LegacySerialCommunicator):
            pass
            # self.flasher = LegacyFirmwareFlasher()
            # TODO change __init__ to not include path
        elif isinstance(device._serial, SerialCommunicator):
            self.flasher = NewFirmwareFlasher(device._serial._writer, device._serial._reader)
        self._updater = updater
        self._device = device
        self._app_state = app_state
        self._parent = parent
        self._view = FlashingView(parent.view)
        super().__init__(self, self._view)
        self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._on_execution_state_changed)

        self._view.set_submit_button_command(self._flash)

    @async_handler
    async def _flash(self) -> None:
        await self._updater.stop()
        self._parent._logger.info("Stopped Update")
        await self._device.execute_command("!FLASH_USB")
        self._parent._logger.info("Executed command FLASH_USB")
        self._parent._logger.info("Sleep for 10s")
        await asyncio.sleep(10)
        self._device._serial._writer.write(b'SYNC')
        await self._device._serial._writer.drain()

        # Read the response (4 bytes)
        response = await self._device._serial._reader.read(4)

        # Check if the response is valid
        if len(response) == 4:
            print(f"Received response: {response}")
        else:
            print(f"Unexpected response length: {len(response)}")
            
        boot_command = b'BOOT'  # "BOOT" as bytes
        zero_value = (0).to_bytes(4, byteorder='big')  # 0 as 4-byte big-endian integer

        # Combine the two parts
        command = boot_command + zero_value
        self._device._serial._writer.write(command)
        await self._device._serial._writer.drain()
        self._parent._logger.info("Start update again")
        self._updater.start()
        #self._device._serial.changeBaudrate()

    def _on_execution_state_changed(self, e: PropertyChangeEvent) -> None:
        pass

class FlashingView(TabView):
    def __init__(self, master: ttk.Frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image_resource(images.SETTINGS_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.FLASHER_LABEL
    
    def _initialize_children(self) -> None:
        FLASH_PADDING: Final[tuple[int, int, int, int]] = (5, 0, 5, 5)
        self._flash_frame: ttk.Labelframe = ttk.Labelframe(
            self, padding=FLASH_PADDING
        )
        #self._baud: ttk.Entry = Entry


        self._browse_flash_file_button: FileBrowseButtonView = FileBrowseButtonView(
            self._flash_frame, text=ui_labels.SPECIFY_PATH_LABEL
        )
        self._submit_button: ttk.Button = ttk.Button(
            self._flash_frame, text=ui_labels.SUBMIT_LABEL, style=ttk.DARK
        )

    def _initialize_publish(self) -> None:
        self._flash_frame.pack(expand=True, fill=ttk.BOTH)
        self._flash_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._flash_frame.rowconfigure(0, weight=sizes.DONT_EXPAND)
        self._flash_frame.rowconfigure(1, weight=sizes.DONT_EXPAND)
        self._browse_flash_file_button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._submit_button.grid(
            row=1,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )

    def set_submit_button_command(self, command: Callable[[], None]) -> None:
        self._submit_button.configure(command=command)

