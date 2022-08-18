from __future__ import annotations

import subprocess
import tkinter as tk
import tkinter.ttk as ttk

from typing import TYPE_CHECKING

import soniccontrol.constants as const

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol._notebook import ScNotebook


class InfoTab(ttk.Frame):
    """
    The InfoTab is the part of the ScNotebook and has the corresping
    information about the SonicControl. Not only does it provide the
    version of the application. It can be used for opening the help
    manual.

    Inheritance:
        ttk (tkinter.ttk.Frame): the basic Frame object
    """

    INFOTEXT = (
        "Welcome to soniccontrol, a light-weight application to\n"
        "control sonicamp systems over the serial interface. \n"
        'For help, click the "Manual" button below\n'
        "\n"
        "(c) usePAT G.m.b.H\n"
    )

    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root

        self.soniccontrol_logo_frame: ttk.Frame = ttk.Frame(self)

        self.soniccontrol_logo1: ttk.Label = ttk.Label(
            self.soniccontrol_logo_frame,
            text="sonic",
            padding=(10, 0, 0, 10),
            font="QTypeOT-CondLight 30",
            borderwidth=-2,
        )

        self.soniccontrol_logo2: ttk.Label = ttk.Label(
            self.soniccontrol_logo_frame,
            text="control",
            padding=(0, 0, 0, 10),
            font="QTypeOT-CondBook 30 bold",
            borderwidth=-2,
        )

        self.info_label: ttk.Label = ttk.Label(self, text=InfoTab.INFOTEXT)

        self.controlframe: ttk.Frame = ttk.Frame(self)

        self.manual_btn: ttk.Button = ttk.Button(
            self.controlframe, text="Help Manual", command=self.open_manual
        )

        self.version_label: ttk.Label = ttk.Label(
            self,
            text=f"Version: {const.VERSION}",
        )

    def publish(self) -> None:
        """
        Publishes the object and children
        """
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)
        self.controlframe.pack()

        self.version_label.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=10)

    def open_manual(self) -> None:
        """
        Opens the helppage manual with the default pdf viewer
        """
        subprocess.Popen(["help_page.pdf"], shell=True)

    def attach_data(self) -> None:
        pass
