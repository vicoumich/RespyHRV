from dash import Input, Output, State, html
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os

def get_layout():
    missing = []
    for name in useful_channel_asr:
        full_path = os.path.join(analysis_path, f"{name}.npy")
        if not os.path.exists(full_path):
            missing.append(f"{name}.npy")

    if missing:
        return html.Div([
            html.H1("Fichiers manquants :"),
            html.Ul([html.Li(f) for f in missing])
        ])
    else:
        return html.Div("Tous les fichiers nécessaires sont présents.")