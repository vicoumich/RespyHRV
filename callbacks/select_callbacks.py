from dash import Input, State, dcc, Output
from callbacks.home_callbacks import UPLOAD_TRACKER
import json
from config import session_path


def register_callbacks(app):
    @app.callback(
        Output('channels-status', 'children'),
        Input('validate-btn', 'n_clicks'),
        State('ecg-dropdown', 'value'),
        State('resp-dropdown', 'value'),
        State('status-dropdown', 'value'),
        State('downsampling-dropdown', 'value'),
        prevent_initial_call=True
    )
    def on_validate(n_clicks, ecg, resp, status, ds_freq):
        # debug
        # print(" Fichier traité:", UPLOAD_TRACKER['last_file'])
        # print(" ECG:", ecg)
        # print(" RESP:", resp)
        # print(" STATUS:", status)
        # fin debug
        channels = {}
        if len(ecg) > 1:
            channels['ecg1'] = ecg[0]
            channels['ecg2'] = ecg[1]
        else:
            channels['ecg'] = ecg[0]
        channels['respi'] = resp
        channels['status'] = status
        UPLOAD_TRACKER['selected_channels'] = channels
        UPLOAD_TRACKER['ds_freq'] = float(ds_freq) if ds_freq != None else 'None'

        # Ajout des channels selectionnées dans le json session
        with open(session_path, 'w') as json_file:
            json.dump(UPLOAD_TRACKER, json_file)
            
        return dcc.Location(pathname='/analyse', id='redirect-after-select')
