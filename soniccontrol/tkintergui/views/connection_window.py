import asyncio
from typing import Callable, Dict, List
from async_tkinter_loop import async_handler
from serial_asyncio import open_serial_connection
import serial.tools.list_ports as list_ports
import ttkbootstrap as ttk
import tkinter as tk

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.sonicpackage.amp_data import Info, Status
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
from soniccontrol.state_updater.logger import Logger
from soniccontrol.tkintergui.utils.constants import (sizes,
                                                     style, ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.device_window import DeviceWindow
from soniccontrol.utils.files import images


class DeviceWindowManager:
    def __init__(self, root):
        self._root = root
        self._id_device_window_counter = 0
        self._opened_device_windows: Dict[int, DeviceWindow] = {}

    def open_device_window(self, sonicamp: SonicAmp, logger: Logger) -> DeviceWindow:
        device_window = DeviceWindow(sonicamp, self._root, logger)
        device_window._view.focus_set() # grab focus and bring window to front
        self._id_device_window_counter += 1
        device_window_id = self._id_device_window_counter
        self._opened_device_windows[device_window_id] = device_window
        device_window.subscribe(
            "close", lambda _: self._opened_device_windows.pop(device_window_id)
        )
        return device_window


class ConnectionWindow(UIComponent):
    def __init__(self):
        self._view: ConnectionWindowView = ConnectionWindowView()
        super().__init__(None, self._view)
        self._device_window_manager = DeviceWindowManager(self._view)
        self._view.set_connect_button_command(lambda: self._attempt_connection())
        self._view.set_refresh_button_command(lambda: self._refresh_ports())
        self._refresh_ports()

    def _refresh_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self._view.set_ports(ports)

    @async_handler
    async def _attempt_connection(self):
        logger = Logger()
        baudrate = 4000 # TODO: change baudrate
        reader, writer = await open_serial_connection(url=self._view.get_url(), baudrate=baudrate)
        serial = SerialCommunicator(log_callback=lambda log: logger.insert_log_to_queue(log))
        await serial.connect(reader, writer)
        sonicamp = await AmpBuilder().build_amp(ser=serial)
        await sonicamp.serial.connection_opened.wait()
        self._device_window_manager.open_device_window(sonicamp, logger)


class ConnectionWindowView(ttk.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._refresh_button: ttk.Button = ttk.Button(
            self._main_frame,
            image=ImageLoader.load_image(
                images.REFRESH_ICON_GREY, sizes.BUTTON_ICON_SIZE
            ),
            style=style.SECONDARY_OUTLINE,
            compound=ttk.RIGHT,
        )
        self._port = tk.StringVar()
        self._ports_menue: ttk.Combobox = ttk.Combobox(
            self._main_frame,
            textvariable=self._port,
            style=ttk.DARK,
            state=ttk.READONLY,
        )
        self._connect_button: ttk.Button = ttk.Button(
            self._main_frame,
            style=ttk.SUCCESS,
            text=ui_labels.CONNECT_LABEL,
        )

        self._main_frame.pack(fill=ttk.BOTH, expand=True)
        self._ports_menue.pack(
            side=ttk.LEFT, expand=True, fill=ttk.X, padx=sizes.SMALL_PADDING
        )
        self._refresh_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)
        self._connect_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)

    def get_url(self) -> str:
        return self._port.get()

    def set_connect_button_command(self, command: Callable[[], None]) -> None:
        self._connect_button.configure(command=command)

    def set_refresh_button_command(self, command: Callable[[], None]) -> None:
        self._refresh_button.configure(command=command)

    def set_ports(self, ports: List[str]) -> None:
        self._ports_menue.configure(values=ports)
