from physio_piezo import compute_rsa
import config


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
    if return_time:
        result['time'] = data['time']
    if return_status:
        result['status'] = data['status']
    return result
    

