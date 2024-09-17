
import asyncio
import logging
from pathlib import Path
from typing import Final, Callable
from soniccontrol_gui.state_fetching.updater import Updater
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import TabView
from sonicpackage.communication.communicator import Communicator
from sonicpackage.communication.serial_communicator import LegacySerialCommunicator, SerialCommunicator
from sonicpackage.flashing.firmware_flasher import LegacyFirmwareFlasher, NewFirmwareFlasher
from sonicpackage.sonicamp_ import SonicAmp

from async_tkinter_loop import async_handler

import ttkbootstrap as ttk

from soniccontrol_gui.constants import sizes, ui_labels
from sonicpackage.events import Event, PropertyChangeEvent
from soniccontrol_gui.views.core.app_state import AppState
from soniccontrol_gui.resources import images
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.widgets.file_browse_button import FileBrowseButtonView
from sonicpackage.system import PLATFORM


class Flashing(UIComponent):
    RECONNECT_EVENT = "Reconnect"
    def __init__(self, parent: UIComponent, logger: logging.Logger, device: SonicAmp | None = None, app_state: AppState | None = None, updater: Updater | None = None, communicator: Communicator | None = None):
        if device:
            if isinstance(device._serial, LegacySerialCommunicator):
                pass
                # self.flasher = LegacyFirmwareFlasher()
                # TODO change __init__ to not include path
            elif isinstance(device._serial, SerialCommunicator):
                self._writer = device._serial._writer
                self._reader = device._serial._reader
        elif communicator and isinstance(communicator, LegacySerialCommunicator):
            self._writer = communicator._writer
            self._reader = communicator._reader
        self._communicator = communicator
        self._updater = updater
        self._device = device
        self._app_state = app_state
        self._view = FlashingView(parent.view)
        super().__init__(self, self._view)
        self._logger = logging.getLogger(logger.name + "." + Flashing.__name__)
        if self._app_state:
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._on_execution_state_changed)

        self._view.set_submit_button_command(self._flash)

    @async_handler
    async def _flash(self) -> None:
        selected_flash_mode = self._view.get_selected_flash_mode()
        selected_file = self._view.get_selected_file_path()
        if selected_file is None:
            self._logger.info(f"No file for flashing selected")
            return
        self._logger.info(f"Selected flash option: {selected_flash_mode}")
        flasher = None
        if selected_flash_mode == ui_labels.FLASH_LEGACY:
            # TODO implement legacy flashing
            self._logger.info("Executed command FLASH_LEGACY")
        elif selected_flash_mode == ui_labels.FLASH_UART_SLOW:
            flasher = NewFirmwareFlasher(self._logger, 9600, selected_file)
            self._logger.info("Executed command FLASH_UART_SLOW")
        elif selected_flash_mode == ui_labels.FLASH_UART_FAST:
            flasher = NewFirmwareFlasher(self._logger, 115200, selected_file)
            self._logger.info("Executed command FLASH_UART_FAST")
        elif selected_flash_mode == ui_labels.FLASH_USB:
            flasher = NewFirmwareFlasher(self._logger, 115200, selected_file)
            self._logger.info("Executed command FLASH_USB")
        if flasher is None:
            self._logger.info("Flasher was not found")
            return
        command = "!" + selected_flash_mode
        if self._device and self._updater and self._reader and isinstance(flasher, NewFirmwareFlasher):
            await self._updater.stop()
            self._logger.info("Stopped Updater")
            
            await self._device.execute_command(command)
            self._logger.info(f"Executed command {command}")
            self._logger.info("Sleep for 10s")
            await asyncio.sleep(10)
            # Read the response (4 bytes)
            response = await self._reader.read(4)
            await self._device.serial.close_communication(True)
        elif self._reader and self._writer and isinstance(flasher, NewFirmwareFlasher):
            command = command.encode(PLATFORM.encoding)
            total_length = len(command)  # TODO Quick fix for sending messages in small chunks
            offset = 0
            chunk_size=30 # Messages longer than 30 characters could not be sent
            delay = 1

            while offset < total_length:
                # Extract a chunk of data
                chunk = command[offset:offset + chunk_size]
                
                # Write the chunk to the writer
                self._writer.write(chunk)
                
                # Drain the writer to ensure it's flushed to the transport
                await self._writer.drain()

                # Move to the next chunk
                offset += chunk_size
                
                # Sleep for the given delay between chunks skip the last pause
                if offset < total_length:
                    # Debugging output
                    self._logger.info(f"[DEBUG] Wrote chunk: {chunk}. Waiting for {delay} seconds before sending the next chunk.")
                    await asyncio.sleep(delay)
                else:
                    self._logger.info(f"[DEBUG] Wrote last chunk: {chunk}.")
                

            self._logger.info("[DEBUG] Finished sending all chunks.")
            self._logger.info(f"Executed command {command}")
            self._logger.info("Sleep for 10s")
            await asyncio.sleep(10)
            # Read the response (4 bytes)
            try:
                response = await asyncio.wait_for(self._reader.read(100), timeout=1)
            except asyncio.TimeoutError:
                pass
            await self._communicator.close_communication(True)

        await flasher.flash_firmware()
        # boot_command = b'BOOT'  # "BOOT" as bytes
        # zero_value = (0).to_bytes(4, byteorder='big')  # 0 as 4-byte big-endian integer  
        # Combine the two parts
        # command = boot_command + zero_value
        # self._writer.write(command)
        # await self._writer.drain()  
        self.emit(Event(Flashing.RECONNECT_EVENT))

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
        self._flash_mode = ttk.StringVar()
        self._flash_mode_combobox: ttk.Combobox = ttk.Combobox(
            self._flash_frame,
            textvariable=self._flash_mode,
            values=ui_labels.FLASH_OPTIONS,  # Use predefined flash options
            state='readonly',
        )
        self._flash_mode_combobox.current(0)  # Set default to the first option


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

        self._flash_mode_combobox.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )


        self._browse_flash_file_button.grid(
            row=1,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._submit_button.grid(
            row=2,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )

    def set_submit_button_command(self, command: Callable[[], None]) -> None:
        self._submit_button.configure(command=command)

    def get_selected_flash_mode(self) -> str:
        return self._flash_mode.get()  # Retrieve the selected flash mode
    
    def get_selected_file_path(self) -> Path | None:
        """Retrieve the file path from the file browse button."""
        return self._browse_flash_file_button.path

