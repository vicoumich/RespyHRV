import plotly.graph_objects as go
import numpy as np
################################################
# Voir si j'utilise go.Scattergl ou go.Scatter #
################################################



# go.Scattergl lague énormément quand sampling rate > 256
def build_fig(time=None, init_signal=None, process_signal=None,
               cycles=None, ecg2=None, clean_ecg2=None, r_spikes=None, 
               title="Cycles respiratoires", is_ds=False, status=None, 
               micro=None, asr=None, time_asr=None) -> go.Figure:
    # status_labels = ['start', 'end', 'start_stress', 'end_stress', 'start_stress_50']
    fig=go.Figure()

    # Ajustement en type somme car bug de Scattergl si trop de points ( > 256)
    scatter_object = go.Scattergl if is_ds else go.Scatter

    if not(status is None):
        # checked = set(list(status.keys())).issubset(set(status_labels))
        # if checked:
            # fig.add_vline(x=time[status['start']], annotation_text="Début enregistrement", 
            # annotation_position="bottom right")
            # fig.add_vline(x=time[status['start_stress_50']], annotation_text="50", 
            #     annotation_position="bottom right")
            # fig.add_vline(x=time[status['start_stress']], annotation_text="Début stress", 
            #     annotation_position="bottom right")
            # fig.add_vline(x=time[status['end_stress']], annotation_text="Fin stress", 
            #     annotation_position="bottom right")
            # fig.add_vline(x=time[status['end']], annotation_text="Fin enregistrement", 
            #     annotation_position="bottom right")
        # print(status)
        for i in range(len(status[50])):
            label_title = "stress" if (i % 2) != 0 else "repos"
            fig.add_vline(x=time[status[50][i]], annotation_text=f"Début {label_title}", 
                annotation_position="bottom right")
            fig.add_vline(x=time[status[70][i]], annotation_text=f"Fin {label_title}", 
                annotation_position="bottom left")
        
    if not(init_signal is None):
        # Courbe originale (bleu)
        fig.add_trace(scatter_object(
            x=time,
            y=init_signal,
            mode="lines",
            name="Respiration brute",
            line=dict(color="blue"),
            # hoverinfo='skip'
        ))
    
    if not(process_signal is None):
        # Courbe traitée (orange)
        fig.add_trace(scatter_object(
            x=time,
            y=process_signal,
            mode="lines",
            name="Respiration traitée",
            line=dict(color="orange"),
            # hoverinfo='skip'
        ))

    if not(cycles is None):
        # Minima (creux) en vert
        fig.add_trace(scatter_object(
            x=time[cycles[:, 0]],
            y=process_signal[cycles[:, 0]],
            mode='markers',
            name='Minima (inspiration)',
            marker=dict(color='green', size=6, symbol='circle'),
            # hoverinfo='text',  # émet l’infobulle pour ce point
            # hovertext=['Minima à {:.2f}s'.format(time[i]) for i in cycles[:,0]]
        ))

        # Maxima (pics) en rouge
        fig.add_trace(scatter_object(
            x=time[cycles[:, 1]],
            y=process_signal[cycles[:, 1]],
            mode='markers',
            name='Maxima (expiration)',
            marker=dict(color='red', size=6, symbol='circle'),
            # hoverinfo='text',  # émet l’infobulle pour ce point
            # hovertext=['Minima à {:.2f}s'.format(time[i]) for i in cycles[:,1]]
        ))
    
    if not(ecg2 is None):
        fig.add_trace(scatter_object(
            x=time,
            y=ecg2,
            mode='lines',
            name="ECG",
            line=dict(color="green")
        ))
    
    if not(clean_ecg2 is None):
        fig.add_trace(scatter_object(
            x=time,
            y=clean_ecg2,
            mode='lines',
            name="ECG clean",
            line=dict(color='red')
        ))
    
    if not(r_spikes is None):
        # Dessine en priorité les points de l'ecg avant nettoyage
        y = clean_ecg2[r_spikes]# ecg2[r_spikes] if not(ecg2 is None) else clean_ecg2[r_spikes]
        fig.add_trace(scatter_object(
            x=time[r_spikes],
            y=y,
            mode='markers',
            name="R spikes",
            marker=dict(color='black')
        ))

    if not(micro is None):
        # Courbe originale (bleu)
        fig.add_trace(scatter_object(
            x=time,
            y=micro,
            mode="lines",
            name="micro",
            line=dict(color="black")
        ))
    ########################################
    ## CHANGER NOM EN FREQUENCE CARDIAQUE ##
    ########################################
    if not(asr is None ) and not(time_asr is None):
        fig.add_trace(scatter_object(
            x=time_asr,
            y=asr,
            mode='lines',
            name='Fréquence cardiaque instantanée',
            line=dict(color="green")
        ))

    # Mise en page
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Temps (s)",
            type="linear",
            rangeslider=dict(visible=True),
        ),
        yaxis=dict(title="Amplitude", 
                   fixedrange=False
        ),
        height=500,
        margin=dict(l=40, r=20, t=50, b=40),
        dragmode="zoom"
    )
    return fig

def normalised_ecg_resp_plot(time: np.ndarray, resp=None, processed_resp=None,
                             cycles=None, ecg=None, processed_ecg=None,
                             r_spikes=None, status=None, micro=None, is_ds=True,
                             asr=None, time_asr=None):
    """
    Normalize data and add différence to plot différent signals on
    a same plotly properly (eg. resp and ecg)
    """

    if not(resp is None):
        resp = 2* ((resp - np.min(resp)) / (np.max(resp) - np.min(resp))) - 2
    
    if not(processed_resp is None):
        processed_resp = 2* ((processed_resp - np.min(processed_resp)) / (np.max(processed_resp) - np.min(processed_resp))) - 2

    if not(ecg is None):
        ecg = 2* ((ecg - np.min(ecg)) / (np.max(ecg) - np.min(ecg)))

    if not(processed_ecg is None):
        processed_ecg = 2* ((processed_ecg - np.min(processed_ecg)) / (np.max(processed_ecg) - np.min(processed_ecg)))

    if not(micro is None):
        beta = 4 if not asr or not time_asr else 6
        micro = 2* ((micro - np.min(micro)) / (np.max(micro) - np.min(micro))) - beta
    
    if not(asr is None) and not(time_asr is None):
        asr = 2* ((asr - np.min(asr)) / (np.max(asr) - np.min(micro))) - 4


    return build_fig(time, resp, processed_resp, cycles, 
              ecg, processed_ecg, r_spikes['peak_index'], 
              title="Respiration et ECG traités", status=status, is_ds=is_ds,
              micro=micro, asr=asr, time_asr=time_asr)


