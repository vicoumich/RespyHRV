from physio_piezo import compute_rsa
import config


def get_asr_data():
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

    return data['time'], rsa_cycles, cyclic_cardiac_rate
    

