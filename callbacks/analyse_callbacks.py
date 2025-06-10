from dash import Input, Output, State, clientside_callback
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os

def register_callbacks(app):
    @app.callback(
        Output('channels-asr', 'children'),
        Input('btn-submit', 'n_clicks')
    )
    def on_validate_cycles(n_clicks):
        print("clicked")

    @app.callback(
        Output('mode-state', 'children'),
        Input('cleaning-mode', 'value'),
    )
    def on_choosing_mode(value):
        print(value)
        if not value:
            return 'No active modification mode'
        return value
    
    app.clientside_callback(
        """
        function(mode, fig) {
            return window.dash_clientside.clientside.toggle_traces(mode, fig);
        }
        """,
        Output('analysis-graph', 'figure'),
        Input('cleaning-mode', 'value'),
        State('analysis-graph', 'figure'),
        prevent_initial_call=True
    )