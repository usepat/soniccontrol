import logging
from typing import Callable, List
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from async_tkinter_loop import async_handler

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.command import Command
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.tkintergui.utils.events import PropertyChangeEvent
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.core.app_state import ExecutionState
from soniccontrol.utils.files import images, files



class SerialMonitor(UIComponent):
    def __init__(self, parent: UIComponent, communicator: Communicator):
        self._logger = logging.getLogger(parent.logger.name + "." + SerialMonitor.__name__)
        super().__init__(parent, SerialMonitorView(parent.view), self._logger)

        self._logger.debug("Create SerialMonitor")
        self._communicator = communicator
        self._command_history: List[str] = []
        self._command_history_index: int = 0
        self.view.set_send_command_button_command(lambda: self._send_command())
        self.view.bind_command_line_input_on_return_pressed(lambda: self._send_command())
        self.view.bind_command_line_input_on_down_pressed(lambda: self._scroll_command_history(False))
        self.view.bind_command_line_input_on_up_pressed(lambda: self._scroll_command_history(True))

    @async_handler
    async def _send_command(self): 
        command_str = self._view.command_line_input.strip()
        self._logger.debug("Command: %s", command_str)
        self._view.command_line_input = ""
        self._view.add_text_line(">>> " + command_str)
        if len(self._command_history) == 0 or command_str != self._command_history[self._command_history_index]:
            self._command_history.append(command_str)
            self._command_history_index = 0
        
        if self._is_internal_command(command_str):
            await self._handle_internal_command(command_str) 
        else:
            answer_str = await self._send_and_receive(command_str)
            self._print_answer(answer_str)

    async def _send_and_receive(self, command_str: str) -> str:
        try:
            answer, _ = await Command(message=command_str).execute(connection=self._communicator)
            return answer.string
        except Exception as e:
            self._logger.error(e)
            await self._communicator.close_communication()
            return str(e)

    def _print_answer(self, answer_str: str):
        self._logger.debug("Answer: %s", answer_str)
        self._view.add_text_line(answer_str)


    def _print_log(self, log_msg: str):
        self._view.add_text_line(log_msg)


    def _is_internal_command(self, command_str: str):
        return command_str in ["clear", "help"]


    async def _handle_internal_command(self, command_str: str) -> None:
        self._logger.debug("Execute internal command")
        if command_str == "clear":
            self._view.clear()
        elif command_str == "help":
            help_text = ""
            if self._communicator.protocol.major_version == 1:
                with open(files.HELPTEXT_SONIC_V1, "r") as file:
                    help_text = file.read()
            else:
                help_text = await self._send_and_receive("?help")
            
            help_text += "\n"
            with open(files.HELPTEXT_INTERNAL_COMMANDS, "r") as file:
                help_text += file.read()
            self._view.add_text_line(help_text)
            

    def _scroll_command_history(self, is_scrolling_up: bool):
        if len(self._command_history) == 0:
            return
        
        self._command_history_index += -1 if is_scrolling_up else +1
        self._command_history_index %= len(self._command_history) 
        self._view.command_line_input = self._command_history[self._command_history_index]


    def on_execution_state_changed(self, e: PropertyChangeEvent) -> None:
        execution_state: ExecutionState = e.new_value
        enabled = execution_state not in [ExecutionState.NOT_RESPONSIVE, ExecutionState.BUSY_FLASHING]
        self._view.set_send_command_button_enabled(enabled)
        self._view.set_command_line_input_enabled(enabled)



class SerialMonitorView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.CONSOLE_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SERIAL_MONITOR_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )
        INPUT_FRAME_PADDING = (3, 1, 3, 4)
        self._input_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.INPUT_LABEL, padding=INPUT_FRAME_PADDING
        )
        self._read_button: ttk.Checkbutton = ttk.Checkbutton(
            self._input_frame,
            text=ui_labels.AUTO_READ_LABEL,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._command_line_input = ttk.StringVar()
        self._command_line_input_field: ttk.Entry = ttk.Entry(self._input_frame, textvariable=self._command_line_input, style=ttk.DARK)
        self._send_button: ttk.Button = ttk.Button(
            self._input_frame,
            text=ui_labels.SEND_LABEL,
            style=ttk.SUCCESS,
            image=ImageLoader.load_image(
                images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(1, weight=sizes.DONT_EXPAND, minsize=40)
        self._output_frame.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._scrolled_frame.pack(
            expand=True,
            fill=ttk.BOTH,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.MEDIUM_PADDING,
        )

        self._input_frame.grid(
            row=1,
            column=0,
            sticky=ttk.EW,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._input_frame.columnconfigure(0, weight=1)
        self._input_frame.columnconfigure(1, weight=10)
        self._input_frame.columnconfigure(2, weight=3)
        self._read_button.grid(
            row=0,
            column=0,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._command_line_input_field.grid(
            row=0,
            column=1,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._send_button.grid(
            row=0,
            column=2,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )

    def set_send_command_button_command(self, command: Callable[[], None]):
        self._send_button.configure(command=command)

    def set_send_command_button_enabled(self, enabled: bool) -> None:
        self._send_button.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)

    def set_command_line_input_enabled(self, enabled: bool) -> None:
        self._command_line_input_field.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)

    @property
    def command_line_input(self) -> str:
        return self._command_line_input.get()

    @command_line_input.setter
    def command_line_input(self, text: str):
        self._command_line_input.set(text)

    def bind_command_line_input_on_down_pressed(self, command: Callable[[], None]):
        self._command_line_input_field.bind("<Down>", lambda _: command()) 

    def bind_command_line_input_on_up_pressed(self, command: Callable[[], None]):
        self._command_line_input_field.bind("<Up>", lambda _: command())

    def bind_command_line_input_on_return_pressed(self, command: Callable[[], None]):
        self._command_line_input_field.bind("<Return>", lambda _: command())

    def add_text_line(self, text: str):
        ttk.Label(self._scrolled_frame, text=text, font=("Consolas", 10)).pack(
            fill=ttk.X, side=ttk.TOP, anchor=ttk.W
        )
        self._scrolled_frame.update()
        self._scrolled_frame.yview_moveto(1)

    def clear(self):
        for child in self._scrolled_frame.winfo_children():
            child.destroy()

