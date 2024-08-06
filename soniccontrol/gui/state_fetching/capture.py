import datetime
import logging

from soniccontrol.sonicpackage.amp_data import Status
from soniccontrol.gui.state_fetching.csv_writer import CsvWriter
from soniccontrol.gui.state_fetching.data_provider import DataProvider


class Capture:
    def __init__(self, logger: logging.Logger = logging.getLogger()):
        self._logger = logging.getLogger(logger.name + "." + Capture.__name__)
        self._is_capturing = False
        self._data_attrs = ["timestamp", "signal", "frequency", "gain", "urms", "irms", "phase", "temperature"]
        self._capture_file_format = "./logs/sonicmeasure-{}.csv"
        self._data_provider = DataProvider()
        self._csv_data_collector = CsvWriter()


    @property 
    def is_capturing(self) -> bool:
        return self._is_capturing
    
    
    @property
    def data_provider(self) -> DataProvider:
        return self._data_provider
    

    def start_capture(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        capture_filename = self._capture_file_format.format(timestamp)
        self._csv_data_collector.open_file(capture_filename, self._data_attrs)
        self._is_capturing = True
        self._logger.info("Start Capture")


    def end_capture(self):
        self._csv_data_collector.close_file()
        self._is_capturing = False
        self._logger.info("End Capture")


    def on_update(self, status: Status):
        if self._is_capturing:
            attrs = {}
            for attr_name in self._data_attrs:
                attrs[attr_name] = getattr(status, attr_name)

            self._data_provider.add_row(attrs)
            self._csv_data_collector.write_entry(attrs)



    