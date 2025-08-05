import os
import base64
import dash
from dash import Input, Output, State, ctx, no_update, dcc, html
import config
from modules.bdf_reader import extract_channels
import json
from config import SESSION_FOLDER
from config import create_session, get_current_session_name, delete_session, set_current_session, is_data
from dash import ALL

# Données transmises à la page select/
UPLOAD_TRACKER = {'last_file': None, 'channels': [], 'session_name': ''}


"""
Callback appelé quand le contenue de l'input à fichier est
modifié, envoie le fichier au serveur qui le sauvegarde si
le format est bon.
"""

def register_callbacks(app: dash.Dash):

    @app.callback(
        Output('upload-status', 'children',  allow_duplicate=True),
        Output('confirm-delete', 'displayed'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def handle_file_upload(contents, filename: str):
        if contents is None or filename is None:
            return no_update

        if not config.allowed_file(filename):
            return "Fichier non autorisé. Veuillez fournir un .bdf."

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            f.write(decoded)

        # Juste le nom de la session
        session_name = filename.split('.')[0]

        # Extraire les channels et stocker l'état
        UPLOAD_TRACKER['last_file'] = file_path
        UPLOAD_TRACKER['channels'] = extract_channels(file_path)
        UPLOAD_TRACKER['session_name'] = session_name
        
        # Le fichier représente une session, stockée en json
        create_code = create_session(session_name, UPLOAD_TRACKER)
        if create_code == 1:
            return no_update, True
        if create_code == 2:
            return no_update, False

        return dcc.Location(pathname='/select', id='redirect-after-upload'), False

    @app.callback(
        Output('confirm-delete', 'submit_n_clicks'),
        Output('upload-status', 'children', allow_duplicate=True),
        Input('confirm-delete', 'submit_n_clicks'),
        prevent_initial_call=True
    )
    def handle_confirm_delete(submit_n_clicks):
        print(submit_n_clicks)
        # Supprime et recréé un nouveau qui a le meme nom
        if submit_n_clicks:
            name = get_current_session_name()
            delete_session(name)
            create_session(name, UPLOAD_TRACKER)
            return 0, dcc.Location(pathname='/select', id='redirect-after-upload')
        return 0, dcc.Location(pathname='/select', id='redirect-after-upload')

    @app.callback(
        Output('dummy-div', 'children'),
        Output('upload-status', 'children'),
        Input({'type': 'session-item', 'index': ALL}, 'n_clicks'),
        State({'type': 'session-item', 'index': ALL}, 'id'),
        prevent_initial_call=True
    )
    def on_click(n_clicks_list, ids):
        # Si aucun déclencheur, on ne fait rien
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        # Méthode recommandée (Dash ≥2.4) :
        triggered = ctx.triggered_id
        clicked_index = triggered['index']
        print("Open: ", clicked_index)
        set_current_session(clicked_index)
        if is_data():
            return no_update, dcc.Location(pathname='/analyse', id='redirect-after-upload')
        else:
            return html.H2("No data found for this session, please drop the file again."), no_update

