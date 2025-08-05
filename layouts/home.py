from dash import html, dcc
from dash import dash_table
from config import clean_session, clean_current_session, get_sessions_names
"""
Affiche l'input pour fichier bdf et le bouton pour regarder
les fichiers présents sur le serveur.
"""
def get_layout():

    # Nettoyage de tous les fichier sutilisés dans
    # une autre session de modification

    ######################
    # NE PAS DECOMMENTER #
    ######################
    # clean_session() ####
    ######################
    ######################

    clean_current_session()
    return html.Div([
        html.H1("Accueil - Upload de fichier BDF"),

        html.Div([
            dcc.ConfirmDialog(
                id='confirm-delete',
                message='A session with this name already exists.\nClick OK to override the saved session',
            ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Glissez un fichier BDF ici ou cliquez pour sélectionner.'
                ]),
                style={
                    'width': '100%',
                    'height': '100px',
                    'lineHeight': '100px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='upload-status')
        ], style={'marginBottom': '40px'}),
        generate_sessions_list()

        # html.Div([
        #     html.H2("Ou consulter les fichiers existants :"),
        #     html.A(
        #         html.Button("Voir les fichiers", style={
        #             'padding': '10px 20px',
        #             'fontSize': '16px',
        #             'borderRadius': '8px',
        #             'backgroundColor': '#007BFF',
        #             'color': 'white',
        #             'border': 'none',
        #             'cursor': 'pointer'
        #         }),
        #         href="/files"
        #     )
        # ])
    ])

def generate_sessions_list():
    names = get_sessions_names() # [1:]
    html_list = html.Ul([
        html.Li(
            name, 
            id={'type': 'session-item', 'index': name}            
        ) for name in names
    ] + [html.Div(id='dummy-div')], className="session-list")
    return html_list