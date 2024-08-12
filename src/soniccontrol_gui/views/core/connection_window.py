from asyncio import StreamReader, StreamWriter
import asyncio
from pathlib import Path
from typing import Callable, Dict, List, Optional, cast
from async_tkinter_loop import async_handler
from serial_asyncio import open_serial_connection
import serial.tools.list_ports as list_ports
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.dialogs.dialogs import Messagebox

from soniccontrol_gui.ui_component import UIComponent
from sonicpackage.builder import AmpBuilder
from sonicpackage.communication.connection_builder import ConnectionBuilder
from sonicpackage.interfaces import Communicator
from sonicpackage.communication.serial_communicator import LegacySerialCommunicator
from sonicpackage.sonicamp_ import SonicAmp
from soniccontrol_gui.state_fetching.logger import create_logger_for_connection
from soniccontrol_gui.utils.animator import Animator, DotAnimationSequence, load_animation
from soniccontrol_gui.constants import sizes, style, ui_labels
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.views.core.device_window import DeviceWindow, KnownDeviceWindow, RescueWindow
from soniccontrol_gui.resources import images
from importlib import resources as rs
import sonicpackage.bin


class DeviceWindowManager:
    def __init__(self, root):
        self._root = root
        self._id_device_window_counter = 0
        self._opened_device_windows: Dict[int, DeviceWindow] = {}

    def open_rescue_window(self, communicator: Communicator, connection_name: str) -> DeviceWindow:
        device_window = RescueWindow(communicator, self._root, connection_name)
        self._open_device_window(device_window)
        return device_window

    def open_known_device_window(self, sonicamp: SonicAmp, connection_name: str) -> DeviceWindow:
        device_window = KnownDeviceWindow(sonicamp, self._root, connection_name)
        self._open_device_window(device_window)
        return device_window
    
    def _open_device_window(self, device_window: DeviceWindow):
        device_window._view.focus_set()  # grab focus and bring window to front
        self._id_device_window_counter += 1
        device_window_id = self._id_device_window_counter
        self._opened_device_windows[device_window_id] = device_window
        device_window.subscribe(
            DeviceWindow.CLOSE_EVENT, lambda _: self._opened_device_windows.pop(device_window_id) #type: ignore
        )


class ConnectionWindow(UIComponent):
    def __init__(self, show_simulation_button=False):
        self._view: ConnectionWindowView = ConnectionWindowView(show_simulation_button)
        super().__init__(None, self._view)

        # set animation decorator
        def set_loading_animation_frame(frame: str) -> None:
            self._view.loading_text = frame
        def on_animation_end() -> None:
            self._view.loading_text = ""
        animation = Animator(DotAnimationSequence("Connecting"), set_loading_animation_frame, 2., done_callback=on_animation_end)
        decorator = load_animation(animation)
        self._attempt_connection = decorator(self._attempt_connection)

        self._device_window_manager = DeviceWindowManager(self._view)
        self._view.set_connect_via_url_button_command(self._on_connect_via_url)
        self._view.set_connect_to_simulation_button_command(self._on_connect_to_simulation)
        self._view.set_refresh_button_command(self._refresh_ports)
        self._refresh_ports()

    def _refresh_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self._view.set_ports(ports)

    @async_handler
    async def _on_connect_via_url(self):
        url = self._view.get_url()
        baudrate = 9600

        reader, writer = await open_serial_connection(
            url=url, baudrate=baudrate
        )

        connection_name = Path(url).name
        await self._attempt_connection(connection_name, reader, writer)

    @async_handler 
    async def _on_connect_to_simulation(self):
        process = await asyncio.create_subprocess_shell(
            str(rs.files(sonicpackage.bin).joinpath("cli_simulation_mvp")),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert(process.stdout is not None)
        assert(process.stdin is not None)

        connection_name = "simulation"
        writer = process.stdin
        reader = process.stdout
        await self._attempt_connection(connection_name, reader, writer)

    async def _attempt_connection(self, connection_name: str, reader: StreamReader, writer: StreamWriter):
        logger = create_logger_for_connection(connection_name)
        logger.debug("Established serial connection")

        try:
            serial, commands = await ConnectionBuilder.build(
                reader=reader,
                writer=writer,
                logger=logger,
            )
            serial.subscribe(serial.DISCONNECTED_EVENT, lambda _e: writer.close())
            logger.debug("Build SonicAmp for device")
            sonicamp = await AmpBuilder().build_amp(ser=serial, commands=commands, logger=logger)
            await sonicamp.serial.connection_opened.wait()
        except ConnectionError as e:
            logger.error(e)
            message = ui_labels.COULD_NOT_CONNECT_MESSAGE.format(str(e))
            user_answer: Optional[str] = cast(Optional[str], Messagebox.yesno(message))
            if user_answer is None or user_answer == "No": 
                return
            
            connection: Communicator = LegacySerialCommunicator(logger=logger) #type: ignore
            await connection.open_communication(reader, writer)
            self._device_window_manager.open_rescue_window(connection, connection_name)
        except Exception as e:
            logger.error(e)
            Messagebox.show_error(str(e))
        else:
            logger.info("Created device successfully, open device window")
            self._device_window_manager.open_known_device_window(sonicamp, connection_name)


class ConnectionWindowView(ttk.Window):
    def __init__(self, show_simulation_button: bool, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        self._url_connection_frame: ttk.Frame = ttk.Frame(self)
        self._refresh_button: ttk.Button = ttk.Button(
            self._url_connection_frame,
            image=ImageLoader.load_image_resource(
                images.REFRESH_ICON_GREY, sizes.BUTTON_ICON_SIZE
            ),
            style=style.SECONDARY_OUTLINE,
            compound=ttk.RIGHT,
        )
        self._port = tk.StringVar()
        self._ports_menue: ttk.Combobox = ttk.Combobox(
            self._url_connection_frame,
            textvariable=self._port,
            style=ttk.DARK,
            state=ttk.READONLY,
        )
        self._connect_via_url_button: ttk.Button = ttk.Button(
            self._url_connection_frame,
            style=ttk.SUCCESS,
            text=ui_labels.CONNECT_LABEL,
        )

        self._connect_to_simulation_button: ttk.Button = ttk.Button(
            self,
            style=ttk.SUCCESS,
            text=ui_labels.CONNECT_TO_SIMULATION_LABEL,
        )

        self._loading_text: ttk.StringVar = ttk.StringVar()
        self._loading_label: ttk.Label = ttk.Label(
            self,
            textvariable=self._loading_text
        )

        self._url_connection_frame.pack(side=ttk.TOP, fill=ttk.X, expand=True, pady=sizes.MEDIUM_PADDING)
        self._ports_menue.pack(
            side=ttk.LEFT, expand=True, fill=ttk.X, padx=sizes.SMALL_PADDING
        )
        self._refresh_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)
        self._connect_via_url_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)

        if show_simulation_button:
            self._connect_to_simulation_button.pack(side=ttk.BOTTOM, fill=ttk.X, padx=sizes.SMALL_PADDING, pady=sizes.MEDIUM_PADDING)

        self._loading_label.pack(side=ttk.TOP, pady=sizes.MEDIUM_PADDING)

    @property
    def loading_text(self) -> str:
        return self._loading_text.get()
    
    @loading_text.setter
    def loading_text(self, value: str) -> None:
        self._loading_text.set(value)

    def get_url(self) -> str:
        return self._port.get()

    def set_connect_via_url_button_command(self, command: Callable[[], None]) -> None:
        self._connect_via_url_button.configure(command=command)

    def set_connect_to_simulation_button_command(self, command: Callable[[], None]) -> None:
        self._connect_to_simulation_button.configure(command=command)

    def set_refresh_button_command(self, command: Callable[[], None]) -> None:
        self._refresh_button.configure(command=command)

    def set_ports(self, ports: List[str]) -> None:
        self._ports_menue.configure(values=ports)
