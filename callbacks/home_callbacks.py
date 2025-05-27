import os
import base64
import dash
from dash import Input, Output, State, ctx, no_update, dcc
import config
from modules.bdf_reader import extract_channels
import json
from config import session_path

# Données transmises à la page select/
UPLOAD_TRACKER = {'last_file': None, 'channels': []}


"""
Callback appelé quand le contenue de l'input à fichier est
modifié, envoie le fichier au serveur qui le sauvegarde si
le format est bon.
"""

def register_callbacks(app: dash.Dash):

    @app.callback(
        Output('upload-status', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def handle_file_upload(contents, filename):
        if contents is None or filename is None:
            return no_update

        if not config.allowed_file(filename):
            return "Fichier non autorisé. Veuillez fournir un .bdf."

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            f.write(decoded)

        # Extraire les channels et stocker l'état
        UPLOAD_TRACKER['last_file'] = file_path
        UPLOAD_TRACKER['channels'] = extract_channels(file_path)

        # Le fichier représente une session, stockée en json
        with open(session_path, 'w') as json_file:
            json.dump(UPLOAD_TRACKER, json_file)

        return dcc.Location(pathname='/select', id='redirect-after-upload')
        # return f"Fichier été enregistré avec succès: {filename}"
