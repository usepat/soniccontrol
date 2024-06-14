import pandas as pd
from soniccontrol.tkintergui.utils.events import EventManager, PropertyChangeEvent
from collections import deque


class DataProvider(EventManager):
    def __init__(self):
        super().__init__()
        self._max_size = 100
        self._data = pd.DataFrame
        self._dataqueue = deque([], maxlen=100)


    @property
    def data(self) -> pd.DataFrame:
        return self._data
    

    def add_row(self, row: dict):
        self._dataqueue.append(row)
        self._data = pd.DataFrame(list(self._dataqueue), columns=row.keys())

        self.emit(PropertyChangeEvent("data", None, self._data))