from dash import html, dcc
# from callbacks.home_callbacks import UPLOAD_TRACKER
import json
import os
from config import session_path


def get_layout():
    # Lecture du fichier de session
    if os.path.exists(session_path):
        with open(session_path, 'r') as session:
            channels = json.load(session)['channels']
    else: channels = []
    # print(channels)

    # Fréquences de DownSampling
    ds_freqs = [1024, 512, 256, 128, 64]

    return html.Div([
        html.H2(f"Sélectionner les canaux intéressants :{channels}"),

        html.Label("ECG (1 ou 2) :"),
        dcc.Dropdown(
            id='ecg-dropdown',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=True
        ),

        html.Br(),

        html.Label("Respiration :"),
        dcc.Dropdown(
            id='resp-dropdown',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),

        html.Label("Status :"),
        dcc.Dropdown(
            id='status-dropdown',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),

        html.Label("DownSampling (dépend du contexte des données, ≤256 recommandé):"),
        dcc.Dropdown(
            id='downsampling-dropdown',
            options=[{'label': ds_freq, 'value': ds_freq} for ds_freq in ds_freqs],
            multi=False
        ),

        html.Br(),

        html.Button("Valider", id='validate-btn'),
        html.Div(id='channels-status')
    ])
