import os

# Cannaux à garder pour le calcul et la visualiisation de l'ASR
# après le nettoyage manuel des cycles
useful_channel_asr = ["clean_ecg_d", "clean_resp_d",
                       "ecg_peaks", 'cycles_d', 'ecg_peaks_d']

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
