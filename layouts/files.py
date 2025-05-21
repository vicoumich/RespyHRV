from dash import html
import os
import config

# Charge les fichiers bdf
def get_layout():
    files = [
            f for f in os.listdir(config.UPLOAD_FOLDER)
            if os.path.isfile(os.path.join(config.UPLOAD_FOLDER, f))
        ]
    
    return html.Div([
        html.H1("Fichiers disponibles dans /uploads"),
        html.Ul([html.Li(f) for f in files]) 
    ])