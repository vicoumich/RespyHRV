import config
from dash import html, dcc
import modules.ploting as pl

def get_layout():
    current_session = config.get_current_session_name()
    if current_session == '':
        return html.Div(["Select or drop a file on ", html.A("/home", href="/home"), "."])
    fig, metrics = pl.gsr_plot_with_metrics()
    return html.Div([dcc.Graph( figure=fig)])
