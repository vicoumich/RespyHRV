import plotly.graph_objects as go
from dash import dcc

def build_fig(time=None, init_signal=None, process_signal=None, cycles=None, ecg2=None, clean_ecg2=None, r_spikes=None) -> go.Figure:
    fig=go.Figure()
    if not(init_signal is None):
        # Courbe originale (bleu)
        fig.add_trace(go.Scatter(
            x=time,
            y=init_signal,
            mode="lines",
            name="Respiration brute",
            line=dict(color="blue")
        ))
    
    if not(process_signal is None):
        # Courbe traitée (orange)
        fig.add_trace(go.Scatter(
            x=time,
            y=process_signal,
            mode="lines",
            name="Respiration traitée",
            line=dict(color="orange")
        ))

    if not(cycles is None):
        # Minima (creux) en vert
        fig.add_trace(go.Scatter(
            x=time[cycles[:, 0]],
            y=process_signal[cycles[:, 0]],
            mode='markers',
            name='Minima (inspiration)',
            marker=dict(color='green', size=6, symbol='circle')
        ))

        # Maxima (pics) en rouge
        fig.add_trace(go.Scatter(
            x=time[cycles[:, 1]],
            y=process_signal[cycles[:, 1]],
            mode='markers',
            name='Maxima (expiration)',
            marker=dict(color='red', size=6, symbol='circle')
        ))
    
    if not(ecg2 is None):
        fig.add_trace(go.Scatter(
            x=time,
            y=ecg2,
            mode='lines',
            name="ECG",
            line=dict(color="green")
        ))
    
    if not(clean_ecg2 is None):
        fig.add_trace(go.Scatter(
            x=time,
            y=clean_ecg2,
            mode='lines',
            name="ECG clean",
            line=dict(color='red')
        ))
    
    if not(r_spikes is None):
        # Dessine en priorité les points de l'ecg avant nettoyage
        y = ecg2[r_spikes] if not(ecg2 is None) else clean_ecg2[r_spikes]
        fig.add_trace(go.Scatter(
            x=time[r_spikes],
            y=y,
            mode='markers',
            name="R spikes",
            marker=dict(color='black')
        ))

    # Mise en page
    fig.update_layout(
    title="Signal de respiration : brut vs traité",
    xaxis=dict(
        title="Temps (s)",
        type="linear",
        rangeslider=dict(visible=True),
    ),
    yaxis=dict(title="Amplitude"),
    height=400,
    margin=dict(l=40, r=20, t=50, b=40)
    )
    return dcc.Graph(figure=fig)