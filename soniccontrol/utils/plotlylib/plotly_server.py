from dash import Dash, html, dash_table, dcc, dependencies
import pandas as pd
import abc


class PlotlyPageFactory:
    @abc.abstractmethod
    def __call__(self, app: Dash):
        pass


class LivePlotFactory(PlotlyPageFactory):
    def __init__(self, figure):
        self._figure = figure

    def __call__(self, app: Dash):
        app.callback(
            dependencies.Output("live-graph", "figure"),
            [dependencies.Input("graph-update", "n_intervals")]
        )(self._update_graph_data)

        return [
            dcc.Graph(id="live-graph", figure=self._figure),
            dcc.Interval(
                id='graph-update',
                interval=1000,  # Update every 1000ms (1 second)
                n_intervals=0
            )
        ]
    
    def _update_graph_data(self, n_intervals: int):
        return self._figure


class LiveTableFactory(PlotlyPageFactory):
    def __init__(self, dataProvider: DataProvider):
        self._dataProvider = dataProvider

    def __call__(self, app: Dash):
        app.callback(
            dependencies.Output("live-graph", "figure"),
            [dependencies.Input("graph-update", "n_intervals")]
        )(self._update_table_data)

        return [
            dash_table.DataTable(data=self._dataProvider.data.to_dict('records'), page_size=10),
            dcc.Interval(
                id='graph-update',
                interval=1000,  # Update every 1000ms (1 second)
                n_intervals=0
            )
        ]
    
    def _update_table_data(self, n_intervals: int):
        return self.data.to_dict("records")


class PlotlyServer:
    def __init__(self):
        self._pages: dict = {}
        self._app = Dash()
        self._app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])

        self._app.callback(
            dependencies.Output("page-content", "children"),
            [dependencies.Input("url", "pathname")]
        )(self._display_page)


    def add_page(self, pathUrl: str, pageFactory: PlotlyPageFactory) -> None:
        self._pages[pathUrl] = pageFactory(self._app)

    def _display_page(self, pathname: str):
        if pathname in self._pages:
            return self._pages[pathname]
        return "404 Page not found!"
    
    def run(self):
        self._app.run(debug=True)

