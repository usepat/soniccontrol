from asyncio import StreamReader, StreamWriter
import asyncio
from typing import Callable, Dict, List
from async_tkinter_loop import async_handler
from serial_asyncio import open_serial_connection
import serial.tools.list_ports as list_ports
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.dialogs.dialogs import Messagebox

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.connection_builder import ConnectionBuilder
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.serial_communicator import LegacySerialCommunicator
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
from soniccontrol.state_updater.logger import create_logger_for_connection
from soniccontrol.tkintergui.utils.animator import Animator, DotAnimationSequence
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.core.device_window import DeviceWindow, KnownDeviceWindow, RescueWindow
from soniccontrol.utils import files
from soniccontrol.utils.files import images


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
        connection_name = self._view.get_url()
        baudrate = 9600

        reader, writer = await open_serial_connection(
            url=connection_name, baudrate=baudrate
        )

        await self._attempt_connection(connection_name, reader, writer)

    @async_handler 
    async def _on_connect_to_simulation(self):
        process = await asyncio.create_subprocess_shell(
            str(files.files.CLI_MVC_MOCK),
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

        def set_loading_animation_frame(frame: str) -> None:
            self._view.loading_text = frame
        animation = Animator(DotAnimationSequence("Connecting"), set_loading_animation_frame, 2.)
        animation.run(num_repeats=-1)
        
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
            Messagebox.show_error(str(e))

            connection: Communicator = LegacySerialCommunicator()
            await connection.open_communication(reader, writer)
            self._device_window_manager.open_rescue_window(connection, connection_name)
        except Exception as e:
            logger.error(e)
            Messagebox.show_error(str(e))
        else:
            logger.info("Created device successfully, open device window")
            self._device_window_manager.open_known_device_window(sonicamp, connection_name)
        finally:
            await animation.stop()
            self._view.loading_text = ""


class ConnectionWindowView(ttk.Window):
    def __init__(self, show_simulation_button: bool, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        self._url_connection_frame: ttk.Frame = ttk.Frame(self)
        self._refresh_button: ttk.Button = ttk.Button(
            self._url_connection_frame,
            image=ImageLoader.load_image(
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
