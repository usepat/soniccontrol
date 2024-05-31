import threading
import pandas as pd

from soniccontrol.utils.plotlylib.plotly_server import DataProvider, LiveTableFactory, PlotlyServer


def main_plotly():
    filepath = "./logs/status_log.csv"
    data = pd.read_csv(filepath)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    dataProvider = DataProvider()
    dataProvider.data = data

    server = PlotlyServer()
    server.add_page("/table", LiveTableFactory(dataProvider))

    server_thread = threading.Thread(target=lambda: server.run())
    server_thread.daemon = True
    server_thread.start()
    
    # TODO: start rest of the program