from dash import Input, State, dcc, Output
from modules.asr import get_asr_data
from modules.ploting import plot_instant_asr, plot_mean_asr_by_phase

def register_callbacks(app):
    
    @app.callback(
        Output('analysis-graph', 'figure', allow_duplicate=True),
        Output('analysis-graph2', 'figure', allow_duplicate=True),
        Input('my-dropdown', 'value'),
        prevent_initial_call=True
    )
    def on_feature(feature):
        data, mean_by_phase = get_asr_data(return_status=True)
        plot2 = plot_mean_asr_by_phase(mean_by_phase, feature)
        return plot_instant_asr(
            data['rsa_cycles']['peak_time'], data['rsa_cycles']['rising_amplitude'],
            20, feature, status=data['status'], time=data['time']
        ), plot2