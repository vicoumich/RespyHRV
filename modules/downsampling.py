from scipy.signal import decimate
import numpy as np


# def downsample_signal(signal: np.ndarray, original_fs: float, target_fs: float = 64.0) -> np.ndarray:
#     """
#     Downsampling un signal sous la forme d'un ndarray avec scipy
#     """
#     if target_fs >= original_fs:
#         raise ValueError("target_fs must be lower than original_fs")

#     decimation_factor = int(original_fs // target_fs)

#     # Vérife meme si deja check dans bdf_reader
#     if decimation_factor < 1:
#         return signal

#     # Fir pour conserver la validité de nos cycles respi
#     return decimate(signal, decimation_factor, ftype='fir', zero_phase=True)

def downsample_signal(sf, ds_freq, time, resp, clean_resp, ecg, clean_ecg, micro, cycles, ecg_peaks, status):
    if ds_freq and ds_freq < sf:
        factor = int(sf // ds_freq)
        time_d = time[::factor]# downsample_signal(time, sf, ds_freq)
        resp_d = resp[::factor] # downsample_signal(resp, sf, ds_freq)
        clean_resp_d = clean_resp[::factor] # downsample_signal(clean_resp, sf, ds_freq)
        ecg_d = ecg[::factor] # downsample_signal(ecg, sf, ds_freq)
        clean_ecg_d = clean_ecg[::factor] # downsample_signal(clean_ecg, sf, ds_freq)
        micro_d = micro[::factor] if micro != None else None
        cycles_d = (cycles // factor).astype(np.int64)
        ecg_peaks_d = (ecg_peaks // factor).astype(np.int64)
        status_d = { k: [int(i // factor) for i in v] for k,v in status.items()} if status != None else None 
        # status = downsample_signal(status, sf, ds_freq)
        # sf = ds_freq
        # ds_freq_i = int(ds_freq)
        return {
            f'resp_d': resp_d,
            f'time_d': time_d,
            f'clean_resp_d': clean_resp_d,
            f'ecg_d': ecg_d,
            f'clean_ecg_d': clean_ecg_d,
            f'cycles_d': cycles_d,
            f'ecg_peaks_d': ecg_peaks_d,
            f'status_d': status_d,
            f'micro_d': micro_d
        }
    
    else:
        raise(f"Down sampling rate ({ds_freq}) is over sampling rate({sf})")