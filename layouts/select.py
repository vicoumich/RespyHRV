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
    prefix = '1-' if channels[0][:2] == '1-' or channels[1][:2] == '1-' else ''

    return html.Div([
        html.H2(f"Sélectionner les canaux intéressants :{channels}"),

        html.Label("ECG (1 ou 2) :"),
        dcc.Dropdown(
            id='ecg-dropdown',
            value= [prefix + 'EXG1-0', prefix + 'EXG2-0'],
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=True
        ),

        html.Br(),

        html.Label("Respiration :"),
        dcc.Dropdown(
            id='resp-dropdown',
            value= prefix + 'Resp',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),

        html.Label("Status :"),
        dcc.Dropdown(
            id='status-dropdown',
            value='Status',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),
        
        html.Label("Micro :"),
        dcc.Dropdown(
            id='micro-dropdown',
            value= prefix + 'micro',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),

        html.Label("GSR :"),
        dcc.Dropdown(
            id='gsr-dropdown',
            value= prefix + 'GSR1',
            options=[{'label': ch, 'value': ch} for ch in channels],
            multi=False
        ),

        html.Br(),

        html.Label("DownSampling (dépend du contexte des données, ≤256 recommandé):"),
        dcc.Dropdown(
            id='downsampling-dropdown',
            options=[{'label': ds_freq, 'value': ds_freq} for ds_freq in ds_freqs],
            value=256,
            multi=False
        ),

        html.Br(),

        html.Button("Valider", id='validate-btn'),
        html.Div(id='channels-status')
    ])
