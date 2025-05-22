from mne.io import read_raw_bdf

def extract_channels(file_name):
    bdf = read_raw_bdf(file_name)
    return list(bdf.ch_names)