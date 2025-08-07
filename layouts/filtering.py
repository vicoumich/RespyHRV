from dash import html, dcc
from config import get_current_session_name, get_current_session_info
from modules.bdf_reader import extract_signals, process_resp
from modules.downsampling import downsample_one_signal
from modules.ploting import plot_filtering
import numpy as np

def get_layout():
    current_session = get_current_session_name()
    if current_session == '':
        return html.Div(["Select or drop a file on ", html.A("/home", href="/home"), "."])

    # info de session
    session_info = get_current_session_info()
    channels  = session_info['channels']
    file_path = session_info['last_file']
    filename  = session_info['last_file'].split('\\')[-1].split('.')[0]
    ds_freq   = float(session_info['ds_freq']) if session_info['ds_freq'] != 'None' else None

    # Récupe respi brut de la session courrante
    resp_brut = extract_signals(file_path, channels, ds_freq)
    sf = resp_brut['sf']
    time = resp_brut['time']
    resp_brut = resp_brut['resp']
    ds_resp_brut = downsample_one_signal(sf, ds_freq, resp_brut)

    # Calcule des variantes du filtre
    max_freqs = np.arange(0.1, 1.01, 0.1)
    signals = {freq: process_resp(resp_brut.copy(), sf, freq) for freq in max_freqs}
    signals = {freq: downsample_one_signal(sf, ds_freq, sig) for freq, sig in signals.items()}
    time = downsample_one_signal(sf, ds_freq, time)
    
    return html.Div([
        html.Button(children=["Save frequency"], id='submit-filtering'),
        dcc.Graph(
            id='signal-slider-graph',
            figure=plot_filtering(time, signals, max_freqs, ds_resp_brut)
        ),
        dcc.Store( id='legend-store' , data=['Respiration', '0.1 Hz'])
    ], id='main-div-filtering')