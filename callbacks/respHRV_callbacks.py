from dash import Input, State, dcc, Output
from modules.asr import get_asr_data
from modules.ploting import plot_instant_asr

def register_callbacks(app):
    
    @app.callback(
        Output('analysis-graph', 'figure', allow_duplicate=True),
        Input('my-dropdown', 'value'),
        prevent_initial_call=True
    )
    def on_feature(feature):
        time, rsa_cycles, cyclic_cardiac_rate = get_asr_data()
        return plot_instant_asr(rsa_cycles['peak_time'], rsa_cycles[feature], 20, feature)