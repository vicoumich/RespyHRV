from scipy.signal import decimate
import numpy as np


def downsample_signal(signal: np.ndarray, original_fs: float, target_fs: float = 64.0) -> np.ndarray:
    """
    Downsampling un signal sous la forme d'un ndarray avec scipy
    """
    if target_fs >= original_fs:
        raise ValueError("target_fs must be lower than original_fs")

    decimation_factor = int(original_fs // target_fs)

    # Vérife meme si deja check dans bdf_reader
    if decimation_factor < 1:
        return signal

    # Fir pour conserver la validité de nos cycles respi
    return decimate(signal, decimation_factor, ftype='fir', zero_phase=True)