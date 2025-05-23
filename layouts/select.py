from dash import html, dcc
# from callbacks.home_callbacks import UPLOAD_TRACKER
import json
import os

session_path = '.\session\session.json'

def get_layout():
    # Lecture du fichier de session
    if os.path.exists('.\session\session.json'):
        with open(session_path, 'r') as session:
            channels = json.load(session)['channels']
    else: channels = []
    # print(channels)

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

        html.Button("Valider", id='validate-btn'),
        html.Div(id='channels-status')
    ])
