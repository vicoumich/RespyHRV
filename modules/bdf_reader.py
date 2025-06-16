from mne.io import read_raw_bdf
import physio_piezo
import numpy as np
from modules.downsampling import downsample_signal
import config

def extract_channels(file_name):
    bdf = read_raw_bdf(file_name)
    return list(bdf.ch_names)

def process_resp(signal, sf: float):
    signal = physio_piezo.preprocess(signal.copy(), sf, band=[0.05, 1.0], normalize=False)
    signal = physio_piezo.smooth_signal(signal, sf)
    return signal

def extract_signals(file_name: str, channels: dict, ds_freq=None):
    """
    Returns ecg, respi, processed respi, sampling rate,
    status and time in seconde.
    """

    # Tente d'abord de lire les données sauvegardées
    if config.is_data():
        # debug
        print("\n\nchargement depuis pickle\n\n")
        # fin debug
        return config.read_data()

    # Sinon lit le fichier bdf
    # debug
    print("\n\nchargement depuis bdf\n\n")
    # fin debug
    bdf = read_raw_bdf(file_name)
    channels = {key: val for key,val in channels.items() if val != None}
    bdf = bdf.pick_channels(list(channels.values()))
    sf  = bdf.info["sfreq"]
    
    if 'ecg' in channels:
        ecg = bdf[channels['ecg']][0].ravel()
    else:
        ecg = bdf[channels['ecg1']][0].ravel() - bdf[channels['ecg2']][0].ravel()

    # Extraction des variables bruts du bdf
    resp = bdf[channels['respi']][0].ravel()
    
    # Calcul des timestamps de stress
    status = bdf[channels['status']][0].ravel()
    try:
        status = extract_timestamps(status, sf, precise_complete=1)
    except:
        status = None
    # Pas de label précis, juste des débuts et des fins 
    # status = {
    #     'start': status[50][0],
    #     'start_stress_50': status[50][1],
    #     'start_stress': status[70][0],
    #     'end_stress': status[50][2],
    #     'end': status[70][1]    
    # }

    # Micro
    micro = bdf[channels['micro']][0].ravel() if channels.get('micro', None)!= None else None

    # Nettoyage des artefactes dans la resp (signal smoothing en gros)
    clean_resp = process_resp(resp.copy(), sf)

    # Variable temps en secondes
    time = np.arange(resp.size) / sf
    
    # extraction des cycles respi et des pics ecg
    cycles = physio_piezo.respiration.detect_cycles_by_extrema(clean_resp, sf, 2.5)
    clean_ecg, ecg_peaks = physio_piezo.compute_ecg(ecg, sf)

    cycles_features = get_cycles_features(clean_resp, sf, cycles)

    # Calcul de la frequence cardiaque instantanéé
    srate_bpm = 100.0 # Fréquence du nouveau signal bpm
    time_bpm  = np.arange(0,  time[-1] + 1/srate_bpm, 1/srate_bpm) 
    instant_bpm = physio_piezo.compute_instantaneous_rate(
        ecg_peaks, time_bpm,
        units='bpm', interpolation_kind='linear'
    )

    # downsample = downsample_signal(sf, ds_freq, time, resp, clean_resp, ecg, clean_ecg, micro,
    #                                cycles, ecg_peaks, status)
    
    data = {
        'resp': resp,
        'status': status,
        'clean_resp': clean_resp,
        'time': time,
        'cycles': cycles,
        'sf': sf,
        'ds_freq': ds_freq,
        'ecg': ecg,
        'clean_ecg': clean_ecg,
        'ecg_peaks': ecg_peaks,
        'micro': micro,
        'cycles_features':cycles_features,
        'time_bpm':time_bpm,
        'instant_bpm': instant_bpm,
        # 'downsample': downsample, 
    }
    # Sauvegarde des cannaux lue
    config.save_data(channels=data.copy())

    return data

def get_downsampled_signals(file_name: str, channels: dict, ds_freq=None):
    data = extract_signals(file_name, channels, ds_freq)
    # debug
    # print("Dans get_downsampled : ", data.keys())
    # fin debug
    ds_data = downsample_signal(data['sf'], ds_freq,
                            data['time'], data['resp'], 
                            data['clean_resp'], data['ecg'],
                            data['clean_ecg'], data['micro'], 
                            data['cycles'], data['ecg_peaks'], 
                            data['status'], data['cycles_features'])
    ds_data['time_bpm'] = data['time_bpm'][:] # copy
    ds_data['instant_bpm'] = data['instant_bpm'][:] # copy
    return ds_data

def extract_timestamps(status, sfreq, target_values=(50, 70), precise_complete=None):
    """
    Renvoie les indexs où le signal status devient une des target_values
    dans le vecteur status.

    Args:
        status (np.ndarray): signal de statut (entiers)
        target_values (tuple): valeurs à détecter

    Returns:
        dict: {valeur: [indexes]}
    """
    timestamps = {val: [] for val in target_values}
    #debug
    # print("\n\n",timestamps)
    # Trouver les indices ou la valeur change
    changes = np.where(np.diff(status) != 0)[0] + 1
    
    # Pour chaque changement, tester si la nouvelle valeur est 50 ou 70
    for idx in changes:
        val = status[idx]
        if val in target_values:
            timestamps[val].append(int(idx))
    #debug
    # print("\n\n",timestamps)
    # Pour les échantillons de sabrina précisémment
    # Ajout d'un 70 manquant 
    if not(precise_complete is None):
        timestamps[70] = list((int(timestamps[70][0]), 
                               int(timestamps[50][2] - 20 * sfreq),
                               int(timestamps[70][-1])))
    
    return timestamps

def get_cycles_features(resp, srate, cycles, baseline=0.0):
    return physio_piezo.respiration.compute_respiration_cycle_features(resp, srate, cycles, baseline)