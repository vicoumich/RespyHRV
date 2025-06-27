from dash import Input, Output, State, html, dcc
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os
from config import is_data
from modules.asr import get_asr_data
from modules.ploting import plot_instant_asr

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
    fig = draw_asr_instant()
    return html.Div(
        [
            html.H2("Visualisation du signal"),
            dcc.Graph(id='analysis-graph', figure=fig)
        ]
    )
    


def draw_asr_instant():
    time, rsa_cycles, cyclic_cardiac_rate = get_asr_data()
    return plot_instant_asr(rsa_cycles['peak_time'], rsa_cycles['rising_slope'], 20)
        