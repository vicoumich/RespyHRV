from dash import html, dcc
from dash import dash_table

"""
Affiche l'input pour fichier bdf et le bouton pour regarder
les fichiers présents sur le serveur.
"""

layout = html.Div([
    html.H1("Accueil - Upload de fichier BDF"),

    html.Div([
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
    ], style={'marginBottom': '40px'})

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