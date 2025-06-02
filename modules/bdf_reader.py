from mne.io import read_raw_bdf
import physio_piezo
import numpy as np
from modules.downsampling import downsample_signal

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
    bdf = read_raw_bdf(file_name)
    bdf = bdf.pick_channels(list(channels.values()))
    sf  = bdf.info["sfreq"]
    
    if 'ecg' in channels:
        ecg = bdf[channels['ecg']][0].ravel()
    else:
        ecg = bdf[channels['ecg1']][0].ravel() - bdf[channels['ecg2']][0].ravel()

    # Extraction des variables bruts du bdf
    resp = bdf[channels['respi']][0].ravel()
    status = bdf[channels['status']][0].ravel()

    # Nettoyage des artefactes dans la resp (signal smoothing en gros)
    clean_resp = process_resp(resp.copy(), sf)

    # Variable temps en secondes
    time = np.arange(resp.size) / sf
    
    # extraction des cycles respi et des pics ecg
    cycles = physio_piezo.respiration.detect_cycles_by_extrema(clean_resp, sf, 2.5)
    clean_ecg, ecg_peaks = physio_piezo.compute_ecg(ecg, sf)

    downsample = {}
    if ds_freq and ds_freq < sf:
        factor = int(sf // ds_freq)
        time_d = time[::factor]# downsample_signal(time, sf, ds_freq)
        resp_d = resp[::factor] # downsample_signal(resp, sf, ds_freq)
        clean_resp_d = clean_resp[::factor] # downsample_signal(clean_resp, sf, ds_freq)
        ecg_d = ecg[::factor] # downsample_signal(ecg, sf, ds_freq)
        clean_ecg_d = clean_ecg[::factor] # downsample_signal(clean_ecg, sf, ds_freq)
        cycles_d = (cycles // factor).astype(np.int64)
        ecg_peaks_d = (ecg_peaks // factor).astype(np.int64)
        # status = downsample_signal(status, sf, ds_freq)
        # sf = ds_freq
        ds_freq_i = int(ds_freq)
        downsample = {
            f'resp_{ds_freq_i}': resp_d,
            f'time_{ds_freq_i}': time_d,
            f'clean_resp_{ds_freq_i}': clean_resp_d,
            f'ecg_{ds_freq_i}': ecg_d,
            f'clean_ecg_{ds_freq_i}': clean_ecg_d,
            f'cycles_{ds_freq_i}': cycles_d,
            f'ecg_peaks_{ds_freq_i}': ecg_peaks_d
        }

    return {
        'resp': resp,
        'status': status,
        'clean_resp': clean_resp,
        'time': time,
        'cycles': cycles,
        'sf': sf,
        'ecg': ecg,
        'clean_ecg': clean_ecg,
        'ecg_peaks': ecg_peaks,
        'downsample': downsample
    }

    