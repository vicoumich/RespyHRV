from dash import Input, Output, State, html, dcc, dash_table
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os
from config import is_data
from modules.asr import get_asr_data
from modules.ploting import plot_instant_asr, plot_mean_asr_by_phase

asr_features = ['peak_value', 'trough_value', 'rising_amplitude',
                'decay_amplitude', 'rising_slope', 'decay_slope']
def get_layout():
    missing = []
    # for name in useful_channel_asr:
    #     full_path = os.path.join(analysis_path, f"{name}.npy")
    #     if not os.path.exists(full_path):
    #         missing.append(f"{name}.npy")

    if not is_data():
        return html.Div(
            html.H1("Go back to /home page and drag and drop a bdf file.")
            )
    fig, mean_by_phase_plot = draw_asr_instant()
    # table = build_table(mean_by_phase)
    return html.Div([
        html.H2("respHRV evolution"),
        html.Div([
            dcc.Graph(id='analysis-graph', figure=fig, style={'flex': '1'}),
            dcc.Dropdown(
                id='my-dropdown',
                options=[{'label': opt, 'value': opt} for opt in asr_features],
                value=asr_features[2],
                clearable=False,
                style={'width': '200px', 'marginLeft': '20px'}
            )
        ], style={'display': 'flex', 'alignItems': 'flex-start'}), 
        dcc.Graph(id='analysis-graph2', figure=mean_by_phase_plot, style={'flex': '1'}),
        
    ])
    
# def build_table(df):
#     return dash_table.DataTable(df[asr_features])

def draw_asr_instant():
    data, mean_by_phase = get_asr_data(return_status=True)
    mean_by_phase_plot = plot_mean_asr_by_phase(mean_by_phase, 'rising_amplitude')
    return plot_instant_asr(
        data['rsa_cycles']['peak_time'], data['rsa_cycles']['rising_amplitude'],
        20, status=data['status'], time=data['time']
    ), mean_by_phase_plot
        