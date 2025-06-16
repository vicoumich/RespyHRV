from dash import Output, Input
from layouts.home import get_layout as home_layout
from layouts.files import get_layout as files_layout
from layouts.select import get_layout as select_layout
from layouts.analyse import get_layout as analyse_layout
from layouts.respHRV import get_layout as respHRV_layout

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
        elif pathname == '/select':
            return select_layout()
        elif pathname == '/analyse':
            return analyse_layout()
        elif pathname == '/respHRV':
            return respHRV_layout()
        else:
            return home_layout()
