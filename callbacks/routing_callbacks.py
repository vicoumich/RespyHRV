from dash import Output, Input
from layouts.home import layout as home_layout
from layouts.files import get_layout as files_layout

"""
Callback appellé lors d'une modification de la valeur de l'url.
Renvoie le bon html (layout) en fonction de l'url.
"""

def register_callbacks(app):
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/files':
            return files_layout()
        else:
            return home_layout
