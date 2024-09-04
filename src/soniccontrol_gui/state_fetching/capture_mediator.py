
from soniccontrol_gui.state_fetching.capture import Capture
from soniccontrol_gui.views.control.editor import Editor
from sonicpackage.events import EventManager


class CaptureMediator(EventManager):
    def __init__(self, capture: Capture):
