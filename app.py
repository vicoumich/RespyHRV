from dash import Dash, html, dcc
from callbacks import home_callbacks, routing_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Div qui va contenir le layout en fonction
# de l'url récupéré par Location
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')  # Ce conteneur sera mis à jour avec la page active
])

# Register callbacks
home_callbacks.register_callbacks(app)
routing_callbacks.register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)  
