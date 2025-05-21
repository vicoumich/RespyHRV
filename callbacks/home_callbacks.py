import os
import base64
import dash
from dash import Input, Output, State, ctx, no_update, dcc
import config

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

        return f"Fichier été enregistré avec succès: {filename}"
