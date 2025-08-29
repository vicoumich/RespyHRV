from dash import html, dcc
import json
import os
import modules.bdf_reader
import modules.ploting
import numpy as np
import pandas as pd
from config import get_current_session_name, get_current_session_info # session_path, analysis_path, useful_channel_asr


def get_layout():
    # Lecture du fichier de session
    # debug
    # print('ok')
    # fin debug
    # if os.path.exists(session_path):
    #     with open(session_path, 'r') as session:
    #         session_info = json.load(session)
    # else: return html.Div([html.H1(f"Aucun fichier session trouvé")])
    
    session_name = get_current_session_name()
    if session_name == '':
        return html.Div(["Select or drop a file on ", html.A("/home", href="/home"), "."])
    session_info = get_current_session_info()
    

    selected_channels = session_info['selected_channels']
    file_path = session_info['last_file']
    filename = session_info['last_file'].split('\\')[-1].split('.')[0]

    # Fréquence de down Sample entrée dans la GUI
    ds_freq   = float(session_info['ds_freq']) if session_info['ds_freq'] != 'None' else None
    # ds_freq_i = int(ds_freq) if not(ds_freq is None ) else None
           
    # Affichage downsamplé ou non en fonction de l'attribut sélectionné sur la GUI
    if ds_freq != None:
        data = modules.bdf_reader.get_downsampled_signals(file_path, selected_channels, ds_freq)
        fig = modules.ploting.normalised_ecg_resp_plot(data[f'time_d'], # modules.ploting.build_fig
                                        data[f'resp_d'], 
                                        data[f'clean_resp_d'],
                                        data[f'cycles_d'],
                                        data[f'ecg_d'],
                                        data[f'clean_ecg_d'],
                                        data[f'ecg_peaks_d'],
                                        data[f'status_d'],
                                        micro=data[f'micro_d'],
                                        is_ds=True, bpm=data['instant_bpm'], 
                                        # gsr=data['gsr_d'],
                                        time_bpm=data['time_bpm'], cycles_on_bpm=False,
                                        title=filename
                                        )
    else: 
        data = modules.bdf_reader.extract_signals(file_path, selected_channels, ds_freq)
        fig = modules.ploting.normalised_ecg_resp_plot(data['time'], data['resp'], 
                                        data['clean_resp'], data['cycles'], data['ecg'],
                                        data['clean_ecg'], data['ecg_peaks'], data['status'],
                                        micro=data['micro'],  is_ds=False, cycles_on_bpm=False) # gsr=data['gsr'],

    # Sauvegarde des données calcul et visu de l'asr
    # _save_for_asr(channels=data)

    return html.Div([
        html.H2("Signals Visualisation"),
        dcc.Graph(id='analysis-graph', figure=fig),
        html.Div([
            html.Button('Change parameters', id='change-params', style={'float':'right', 'marginBottom':'10px'}),
            html.Div(
                id='param-container',
                style={'display':'none', 'float':'right'},
                children=[
                    dcc.Input(
                        id='distance-cycle',
                        type='number',
                        placeholder='Distance cycle',
                        debounce=True,
                        style={'marginRight':'10px'}
                    ),
                    dcc.Input(
                        id='factor-mad',
                        type='number',
                        placeholder='Factor MAD',
                        debounce=True,
                        style={'marginRight':'10px'}
                    ),
                    html.Button('Apply parameters', id='submit-params')
                ]
            )
        ], style={'width':'100%', 'overflow':'hidden'}),

        # Storage des move modifs
        dcc.Store(id='move-store', data={
            'phase': 'start',         # 'start' ou 'select_resp'
            'current_cycle': None,    # stocke {x_old, y_old, traceName, pointIndex}
            'pairs': []               # liste de {old, new}
        }),

        # Storage des delete modifs
        dcc.Store(id='delete-store', data={
            'phase': 'start',         # 'start' ou 'end'
            'start': None,           # stocke {x_start, y_start, traceName, pointIndex}
            'pairs': []               # liste de {start, end}
        }),

        # Storage des add modifs
        dcc.Store(id='add-store', data={
            'phase': 'start',
            'first': None,         # 'expi' ou 'inspi'
            'point': None,         # x,y
            'pairs': []               # liste de {start, end}
        }),

        dcc.Store(id='delete-Rpeak-store', data={
        #    'time': None,
           'peaks': []
        }),

        dcc.RadioItems(
            id='cleaning-mode',
            options=[
                {'label': 'Move', 'value': 'move'}, 
                {'label': 'Delete', 'value': 'delete'},
                {'label': 'Add', 'value': 'add'},
                {'label': 'Delete R-peak', 'value': 'delete-Rpeak'}
            ],
            inline=True
        ),
        
        html.Br(),
        html.Div(children='Modification mode :'),
        html.Div(id='mode-state', children='No active modification mode'),
        html.Br(),
        html.Div(id='log'),
        html.Br(),
        html.Button('Apply modifications', id='btn-submit'),
        html.Div(id='channels-asr')
    ])
    

