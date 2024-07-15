from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness
from typing import Any, Callable
import soniccontrol.tkintergui.models as models
from soniccontrol import soniccontrol_logger as logger
from soniccontrol.tkintergui.mainview import MainView
from soniccontrol.tkintergui.utils.constants import events, tk_const
from soniccontrol.utils.system import PLATFORM, System
from soniccontrol.tkintergui.utils.events import EventManager, PropertyChangeEvent, Event




class SonicController:
    def __init__(self, view: MainView, model: models.DeviceModel):
        self._view: MainView = view
        self._model: models.DeviceModel = model
        self._event_manager = EventManager()

        self._property_listeners: dict[str, Callable[[PropertyChangeEvent], None]] = {
            "freq_khz": self._view.on_frequency_change,
            "gain": self._view.on_gain_change,
            "temperature": self._view.on_temp_change,
            "signal": self._view.on_signal_change,
            "urms": self._view.on_urms_change,
            "irms": self._view.on_irms_change,
            "phase": self._view.on_phase_change,
            "wipe_mode": self._view.on_wipe_mode_change,
            "relay_mode": self._view.on_relay_mode_change,
        }

        self._event_listeners: dict[str, Callable[[Event], None]] = {
            events.CONNECTION_ATTEMPT_EVENT: self._view.on_connection_attempt_event,
            events.CONNECTED_EVENT: self._view.on_connection_established_event,
            events.DISCONNECTED_EVENT: self._view.on_disconnection_event,
            events.SCRIPT_START_EVENT: self._view.on_script_start_event,
            events.SCRIPT_STOP_EVENT: self._view.on_script_stop_event,
            events.FIRMWARE_FLASH_EVENT: self._view.on_firmware_flash_event,
            events.SONICMEASURE_START_EVENT: self._view.on_sonicmeasure_start_event,
            events.SONICMEASURE_STOP_EVENT: self._view.on_sonicmeasure_stop_event,
            events.SCRIPT_PAUSE_EVENT: self._view.on_script_pause_event,
            events.AUTO_MODE_EVENT: self._view.on_auto_mode_event,
            events.SAVE_CONFIG: self._view.on_save_config_event,
        }

        for property_name, listener in self._property_listeners.items():
            self._event_manager.subscribe_property_listener(
                property_name, listener
            )
        
        self._model.status_model.freq_khz.trace_add(
            tk_const.WRITE,
            lambda _, __, ___: self._event_manager.emit(
                PropertyChangeEvent("freq_khz", None, self._model.status_model.freq_khz.get())
            )
        )

        for event_type, listener in self._event_listeners.items():
            self._event_manager.subscribe(
                event_type, listener
            )

        self._view.views.connection._connect_button.configure(
            command=lambda: self._event_manager.emit(
                Event(events.CONNECTION_ATTEMPT_EVENT, data=None)
            )
        )

        self._view.bind_all(
            events.RESIZING_EVENT,
            self._view.resize,
            add=True,
        )

        self._model.status_model.freq_khz.set(1000.000)

    def start(self):
        if PLATFORM != System.WINDOWS:
            logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
            enable_high_dpi_awareness(self._view)
        async_mainloop(self._view)
