from dash import html, dcc
import json
import os
import modules.bdf_reader
import modules.ploting
import numpy as np

session_path = '.\session\session.json'

def get_layout():
    # Lecture du fichier de session
    # debug
    # print('ok')
    # fin debug
    if os.path.exists('.\session\session.json'):
        with open(session_path, 'r') as session:
            session_info = json.load(session)
    else: return html.Div([html.H1(f"Aucun fichier session trouvé dans {session_path}")])
    
    selected_channels = session_info['selected_channels']
    file_path = session_info['last_file']
    
    data = modules.bdf_reader.extract_signals(file_path, selected_channels)

    # debug
    to_print = ['resp', 'status', 'clean_resp', 'time']
    printing = [f"key: {k}, value: {len(data[k])}" for k in to_print]
    # fin debug
    fig = modules.ploting.build_fig(data['time'], data['resp'], data['clean_resp'], data['cycles'])
    return  fig # html.Div(f"channels select:{printing} ")
    
