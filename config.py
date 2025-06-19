import os
import numpy as np
import pandas as pd
import json
import pickle
import shutil


# Cannaux à garder pour le calcul et la visualiisation de l'ASR
# après le nettoyage manuel des cycles
useful_channel_asr = [
    'resp', 'clean_resp', 'status',
    'time', 'ecg', 'clean_ecg',
    'micro', 'ecg_peaks', 'time_bpm',
    'instant_bpm', 'cycles'
]

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'bdf'}
CURRENT_FOLDER = os.getcwd()
SESSION_FOLDER = os.path.join(CURRENT_FOLDER, 'session')
session_path = os.path.join(SESSION_FOLDER, 'session.json')
analysis_path = os.path.join(SESSION_FOLDER, 'data')

# Ensure the folder exists
os.makedirs(SESSION_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(analysis_path, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_data(channels, folder=analysis_path) -> None:

    # Supression des cycles car sauvegardés en .pkl à part
    cycles = channels.pop('cycles_features')
    cycles.to_pickle(os.path.join(folder, f'cycles_features.pkl'))

    # Supression des ecg_peaks car sauvegardés en .pkl à part
    ecg_peaks = channels.pop('ecg_peaks')
    ecg_peaks.to_pickle(os.path.join(folder, 'ecg_peaks.pkl'))

    data = {}
    for channel in useful_channel_asr:
        signal = channels.get(channel, None)
        if isinstance(signal, np.ndarray):
            # debug
            # print("\n\nsaved : ", channel)
            # end
            data[channel] = signal

    # Sauvegarde en pickle des données
    # pour I/O plus rapides
    with open(os.path.join(folder, "extracted_data.pkl"), 'wb') as file:
        pickle.dump(data, file)

    # Sauvegarde des données de fréquences
    freq_data = {'sf': channels['sf'], 'ds_freq': channels['ds_freq']}
    freq_path = os.path.join(folder, "freq.json")
    with open(freq_path, 'w') as json_file:
        json.dump(freq_data, json_file)

    # Sauvegarde des status
    status_path = os.path.join(folder, "status.pkl")
    with open(status_path, 'wb') as file: 
        pickle.dump(channels['status'], file)
    

def is_data(
        folder=analysis_path, 
        files=[
            "cycles_features.pkl", "extracted_data.pkl",
            "freq.json", "ecg_peaks.pkl", "status.pkl"
        ]
    ) -> bool:
    
    file_names = files
    paths = [os.path.join(folder, name) for name in file_names]
    for path_name in paths:
        if not os.path.exists(path_name):
            return False
    return True


def read_data(
        folder=analysis_path, freq_file="freq.json",
        cycles_file="cycles_features.pkl", data_file="extracted_data.pkl",
        ecg_peaks_file="ecg_peaks.pkl", status_file="status.pkl"
) -> None:

    data_path = os.path.join(folder, data_file)
    freq_path = os.path.join(folder, freq_file)
    cycles_path = os.path.join(folder, cycles_file)
    ecg_peaks_path = os.path.join(folder, ecg_peaks_file)
    status_path = os.path.join(folder, status_file)
    
    # Lecture des données 
    with open(data_path, 'rb') as file:
        data = pickle.load(file)
    with open(status_path, 'rb') as file:
        data['status'] = pickle.load(file)

    data['cycles_features'] = pd.read_pickle(cycles_path)
    data['ecg_peaks'] = pd.read_pickle(ecg_peaks_path)

    with open(freq_path, 'r') as file:
        freqs = json.load(file)
    
    data['sf'] = freqs['sf']
    data['ds_freq'] = freqs['ds_freq'] if freqs['ds_freq'] != 'None' else None

    # debug
    # print(data['ecg_peaks'])
    # fin debug

    return data 


def clean_session(
    uploads_dir: str = UPLOAD_FOLDER,
    session_dir: str = SESSION_FOLDER
) -> None:
    """
    Supprime complètement les dossiers `uploads` et `session` (et leur contenu),
    puis les recrée vides.
    """
    for d in (uploads_dir, session_dir):
        # si le dossier existe, on le supprime avec tout son contenu
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
            except OSError as e:
                print(f"Impossible de supprimer {d} : {e}")
        # on recrée un dossier vide
        os.makedirs(d, exist_ok=True)
    os.makedirs(analysis_path, exist_ok=True)
    