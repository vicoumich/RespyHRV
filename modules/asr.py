from physio_piezo import compute_rsa
import config
import pandas as pd
import copy
import os


def get_asr_data(return_time=True, return_status=False):
    """
        Retourne des données asr à afficher et les sauvegarde.
    """

    data = config.read_data()
    ecg_peaks = data['ecg_peaks']
    clean_resp = data['clean_resp']
    cycles_features = data['cycles_features']
    point_per_cycle = 50
    rsa_cycles, cyclic_cardiac_rate = compute_rsa(
        cycles_features,  # nos cycles respiration
        ecg_peaks,
        points_per_cycle=point_per_cycle
    )
    result = {
        'rsa_cycles': rsa_cycles,
        'cyclic_cardiac_rate': cyclic_cardiac_rate,
    }

    ######## Sauvegarde ASR ########
    status = data['status']
    sf = data['sf']
    mean_by_phase = save_data_by_phase(copy.deepcopy(rsa_cycles), copy.deepcopy(status), sf)

    if return_time:
        result['time'] = data['time']
    if return_status:
        result['status'] = data['status']
    return result, mean_by_phase
    

    
def _mean_metrics_in_peak_range(df: pd.DataFrame, a: float, b: float) -> pd.Series:
    mask = df["peak_time"].between(a, b, inclusive="both")
    return pd.DataFrame(df.loc[mask].mean(numeric_only=True)).T


def save_data_by_phase(rsa_cycles:pd.DataFrame, status: dict, sampling_rate: int):
    """
    Save respHRV by phase
    """
    # Récupe id sujet et session
    name = config.get_current_session_name()
    path = os.path.join(os.path.join(config.SESSION_FOLDER, name), 'data')
    #####

    status[50] = [int(v / (sampling_rate)) for v in status[50]]
    status[70] = [int(v / (sampling_rate)) for v in status[70]]
    # print(f"\n\n\n\n\n\n\nstatus: {status}")
    phases = ['repos1', 'stress', 'repos2']
    result = {}

    for i, phase in enumerate(phases, start=0):
        means = _mean_metrics_in_peak_range(rsa_cycles, status[50][i], status[70][i])
        # print("type = ", type(means))
        means['phase'] = phase
        result[phase] = means
        
        # print(result[phase])

    longdf = pd.concat(result.values())
    print(longdf)
    longdf.to_csv(os.path.join(path, 'ASR_by_phase.csv'))

    return longdf
    
    

