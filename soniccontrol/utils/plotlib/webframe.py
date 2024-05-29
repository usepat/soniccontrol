import ctypes
from cefpython3 import cefpython as cef
import tkinter as tk
import sys
import os
import platform


WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# see https://stackoverflow.com/questions/46571448/is-it-possible-to-render-html-in-tkinter/53394551#53394551
class WebFrame(tk.Frame):
    def __init__(self, master):
        self.browser = None
        self.url = "TODO" # TODO
        super().__init__(self, master)

    def embed_browser(self):
        window_info = cef.WindowInfo()
        window_handle = self.winfo_id() # could lead to errors on mac
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(window_handle, rect)
        self.browser = cef.CreateBrowserSync(window_info, url=self.url)

        assert self.browser
        self.message_loop_work()

    def get_browser(self):
        if self.browser:
            return self.browser
        return None

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work) # calls itself inside the tkinter event loop

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.browser = None
        self.destroy()
