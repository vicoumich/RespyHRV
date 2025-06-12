from dash import html, dcc
import json
import os
import modules.bdf_reader
import modules.ploting
import numpy as np
import pandas as pd
from config import session_path, analysis_path, useful_channel_asr


def get_layout():
    # Lecture du fichier de session
    # debug
    # print('ok')
    # fin debug
    if os.path.exists(session_path):
        with open(session_path, 'r') as session:
            session_info = json.load(session)
    else: return html.Div([html.H1(f"Aucun fichier session trouvé")])
    
    selected_channels = session_info['selected_channels']
    file_path = session_info['last_file']

    # Fréquence de down Sample entrée dans la GUI
    ds_freq   = float(session_info['ds_freq']) if session_info['ds_freq'] != 'None' else None
    # ds_freq_i = int(ds_freq) if not(ds_freq is None ) else None
    
    data = modules.bdf_reader.extract_signals(file_path, selected_channels, ds_freq)
       
    # Affichage downsamplé ou non en fonction de l'attribut sélectionné sur la GUI
    if ds_freq != None:
        fig = modules.ploting.normalised_ecg_resp_plot(data['downsample'][f'time_d'], # modules.ploting.build_fig
                                        data['downsample'][f'resp_d'], 
                                        data['downsample'][f'clean_resp_d'],
                                        data['downsample'][f'cycles_d'],
                                        data['downsample'][f'ecg_d'],
                                        data['downsample'][f'clean_ecg_d'],
                                        data['downsample'][f'ecg_peaks_d'],
                                        data['downsample'][f'status_d'],
                                        micro=data['downsample'][f'micro_d'],
                                        is_ds=True, bpm=data['instant_bpm'], 
                                        time_bpm=data['time_bpm'], cycles_on_bpm=False
                                        )
    else: 
        fig = modules.ploting.normalised_ecg_resp_plot(data['time'], data['resp'], 
                                        data['clean_resp'], data['cycles'], data['ecg'],
                                        data['clean_ecg'], data['ecg_peaks'], data['status'],
                                        micro=data['micro'], is_ds=False)

    # Sauvegarde des données calcul et visu de l'asr
    _save_for_asr(channels=data)

    return html.Div([
        html.H2("Visualisation du signal"),
        dcc.Graph(id='analysis-graph', figure=fig),

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

        dcc.RadioItems(
            id='cleaning-mode',
            options=[
                {'label': 'Move', 'value': 'move'}, 
                {'label': 'Delete', 'value': 'delete'},
                {'label': 'Add', 'value': 'add'}
            ],
            inline=True
        ),
        
        html.Br(),
        html.Div(children='Modification mode :'),
        html.Div(id='mode-state', children='No active modification mode'),
        html.Br(),
        html.Div(id='log'),
        html.Br(),
        html.Button('Valider modifications', id='btn-submit'),
        html.Div(id='channels-asr')
    ])
    

def _save_for_asr(channels, folder=analysis_path):

    # Supression des cycles dans car sauvegardés en .pkl et non .npy
    cycles = channels.pop('cycles_features')
    cycles.to_pickle(os.path.join(folder, f'cycles_features.pkl'))
    
    for name in useful_channel_asr:
        signal = channels[name] if name[-2:] != '_d' else channels['downsample'][name]
        np.save(os.path.join(folder, f'{name}.npy'), signal, allow_pickle=False)
