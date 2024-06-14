
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.tkintergui.utils.events import PropertyChangeEvent
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.scrolled import ScrolledFrame
import pandas as pd


class CsvTable(UIComponent):
    def __init__(self, parent: UIComponent):
        super().__init__(parent, CsvTableView(parent.view))

    def on_update_data(self, e: PropertyChangeEvent):
        dataFrame: pd.DataFrame = e.new_value
        dataFrame["timestamp"] = dataFrame["timestamp"].apply(lambda x: x.strftime('%Y/%m/%d-%H:%M:%S'))
        columns = [{"text": column, "stretch": True} for column in dataFrame.columns]
        row_data = dataFrame.to_records(index=False).tolist()
        self.view.set_csv_data(columns, row_data)


class CsvTableView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._csv_table: Tableview = Tableview(self, searchable=True, paginated=False)
        self._csv_table.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)

    def set_csv_data(self, col_data: list, row_data: list) -> None:
        self._csv_table.build_table_data(col_data, row_data)