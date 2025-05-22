from dash import Input, State
from callbacks.home_callbacks import UPLOAD_TRACKER

def register_callbacks(app):
    @app.callback(
        Input('validate-btn', 'n_clicks'),
        State('ecg-dropdown', 'value'),
        State('resp-dropdown', 'value'),
        State('status-dropdown', 'value'),
        prevent_initial_call=True
    )
    def on_validate(n_clicks, ecg, resp, status):
        print("✅ Fichier traité:", UPLOAD_TRACKER['last_file'])
        print("➡️ ECG:", ecg)
        print("➡️ RESP:", resp)
        print("➡️ STATUS:", status)
