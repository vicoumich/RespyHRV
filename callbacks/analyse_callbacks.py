from dash import Input, Output, State
import plotly.graph_objects as go

def register_callbacks(app):
    @app.callback(
        Output('analysis-graph', 'figure'),
        Input('signal-toggle', 'value'),
        State('analysis-graph', 'figure'),
        prevent_initial_call=True
    )
    def toggle_traces(selected_names, fig):
        # reconstruit la Figure Plotly
        # fig = go.Figure(existing_fig)
        # pour chaque trace, on ajuste visible=True ou legendonly
        for trace in fig["data"]:
            trace["visible"] = True if trace["name"] in selected_names else 'legendonly'
        return fig
