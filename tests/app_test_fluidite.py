import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go

# Parametres
DURATION_MINUTES = 21
SAMPLING_RATES = [2048, 1024, 512, 256, 128, 64]  # Liste de frequences d'echantillonnage

duration_seconds = DURATION_MINUTES * 60

data_dict = {}

# Generation des signaux a differentes frequences
t_full = np.linspace(0, duration_seconds, duration_seconds * 2048)
signal_full = np.sin(2 * np.pi * 0.25 * t_full) + 0.1 * np.random.randn(len(t_full))

for rate in SAMPLING_RATES:
    t_down = np.linspace(0, duration_seconds, duration_seconds * rate)
    signal_down = np.sin(2 * np.pi * 0.25 * t_down) + 0.1 * np.random.randn(len(t_down))
    data_dict[str(rate)] = {'t': t_down, 'signal': signal_down}

# Application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualisation des signaux respiratoires"),
    dcc.Dropdown(
        id='sampling-dropdown',
        options=[{'label': f'{rate} Hz', 'value': str(rate)} for rate in SAMPLING_RATES],
        value=str(SAMPLING_RATES[0])
    ),
    dcc.Graph(id='signal-graph')
])

@app.callback(
    Output('signal-graph', 'figure'),
    Input('sampling-dropdown', 'value')
)

def update_graph(selected_rate):
    t = data_dict[selected_rate]['t']
    signal = data_dict[selected_rate]['signal']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=signal, mode='lines', name=f'{selected_rate} Hz'))
    fig.update_layout(
        xaxis=dict(
        title="Temps (s)",
        type="linear",
        rangeslider=dict(visible=True),
        ),
        yaxis_title='Amplitude',
        title=f'Signal respiratoire à {selected_rate} Hz',
        height=600
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
