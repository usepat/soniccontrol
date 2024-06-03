import datetime

from soniccontrol.sonicpackage.amp_data import Status
from soniccontrol.state_updater.csv_writer import CsvWriter
from soniccontrol.state_updater.data_provider import DataProvider


class Capture:
    def __init__(self):
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
        capture_filename = self._capture_file_format % datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self._csv_data_collector.open_file(capture_filename, self._data_attrs)
        self._is_capturing = True


    def end_capture(self):
        self._csv_data_collector.close_file()
        self._is_capturing = False


    def on_update(self, status: Status):
        if self._is_capturing:
            attrs = {}
            for attr_name in self._data_attrs:
                attrs[attr_name] = getattr(status, attr_name)

            self._data_provider.add_row(attrs)
            self._csv_data_collector.write_entry(attrs)



    