from dash import Input, Output, State, html
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os
# def register_callbacks(app):
#     @app.callback(
#         Output('analysis-graph', 'figure'),
#         Input('signal-toggle', 'value'),
#         State('analysis-graph', 'figure'),
#         prevent_initial_call=True
#     )
#     def toggle_traces(selected_names, fig):
#         # reconstruit la Figure Plotly
#         # fig = go.Figure(existing_fig)
#         # pour chaque trace, on ajuste visible=True ou legendonly
#         for trace in fig["data"]:
#             trace["visible"] = True if trace["name"] in selected_names else 'legendonly'
#         return fig

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