from dash import html, dcc
import json
import os
import modules.bdf_reader
import modules.ploting
import numpy as np
from config import session_path


def get_layout():
    # Lecture du fichier de session
    # debug
    # print('ok')
    # fin debug
    if os.path.exists(session_path):
        with open(session_path, 'r') as session:
            session_info = json.load(session)
    else: return html.Div([html.H1(f"Aucun fichier session trouvé dans {session_path}")])
    
    selected_channels = session_info['selected_channels']
    file_path = session_info['last_file']

    # Fréquence de down Sample entrée dans la GUI
    ds_freq   = float(session_info['ds_freq']) if session_info['ds_freq'] != 'None' else None
    ds_freq_i = int(ds_freq) if not(ds_freq is None ) else None
    
    data = modules.bdf_reader.extract_signals(file_path, selected_channels, ds_freq)
    
    # Affichage downsamplé ou non en fonction de l'attribut sélectionné sur la GUI
    if ds_freq != None:
        fig = modules.ploting.build_fig(data['downsample'][f'time_{ds_freq_i}'], 
                                        data['downsample'][f'resp_{ds_freq_i}'], 
                                        data['downsample'][f'clean_resp_{ds_freq_i}'],
                                        data['downsample'][f'cycles_{ds_freq_i}'], is_ds=True)
    else: 
        fig = modules.ploting.build_fig(data['time'], data['resp'], data['clean_resp'], data['cycles'])

    return  dcc.Graph(figure=fig) # html.Div(f"channels select:{printing} ")
    
