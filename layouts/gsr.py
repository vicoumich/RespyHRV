import config
from dash import html, dcc
import modules.ploting as pl

def get_layout():
    current_session = config.get_current_session_name()
    if current_session == '':
        return html.Div(["Select or drop a file on ", html.A("/home", href="/home"), "."])
    if not config.is_gsr_data():
        return html.Div(["No gsr data found."])
    # data = config.read_data()
    #fig = pl.gsr_plot(data["raw_scr_pics"], data["gsr"], data["sf"], data["ds_freq"])
    fig, _ = pl.gsr_plot_with_metrics()
    return html.Div([dcc.Graph( figure=fig)])
