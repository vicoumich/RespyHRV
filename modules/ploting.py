import plotly.graph_objects as go
import numpy as np
import pandas as pd
import config
################################################
# Voir si j'utilise go.Scattergl ou go.Scatter #
################################################



# go.Scattergl lague énormément quand sampling rate > 256
def build_fig(time=None, init_signal=None, process_signal=None,
               cycles=None, ecg2=None, clean_ecg2=None, r_spikes=None, 
               title="Signals", is_ds=False, status=None, 
               micro=None, bpm=None, time_bpm=None, cycles_on_bpm=True, gsr=None) -> go.Figure:
    """
        Génère un plot avec les signaux passés en paramètre
    """
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
            label_title = "stress" if (i % 2) != 0 else "rest"
            fig.add_vline(x=time[status[50][i]], annotation_text=f"Start {label_title}", 
                annotation_position="bottom right")
            fig.add_vline(x=time[status[70][i]], annotation_text=f"End {label_title}", 
                annotation_position="bottom left")
        
    if not(init_signal is None):
        # Courbe originale (bleu)
        fig.add_trace(scatter_object(
            x=time,
            y=init_signal,
            mode="lines",
            name="Respiration",
            line=dict(color="blue"),
            # hoverinfo='skip'
        ))
    
    if not(process_signal is None):
        # Courbe traitée (orange)
        fig.add_trace(scatter_object(
            x=time,
            y=process_signal,
            mode="lines",
            name="Filtered Respiration",
            line=dict(color="orange"),
            # hoverinfo='skip'
        ))

    if not(cycles is None):
        # Minima (creux) en vert
        fig.add_trace(scatter_object(
            x=time[cycles[:, 0]],
            y=process_signal[cycles[:, 0]],
            mode='markers',
            name='Minima (start inspiration)',
            marker=dict(color='green', size=6, symbol='circle'),
            # hoverinfo='text',  # émet l’infobulle pour ce point
            # hovertext=['Minima à {:.2f}s'.format(time[i]) for i in cycles[:,0]]
        ))

        # Maxima (pics) en rouge
        fig.add_trace(scatter_object(
            x=time[cycles[:, 1]],
            y=process_signal[cycles[:, 1]],
            mode='markers',
            name='Maxima (start expiration)',
            marker=dict(color='red', size=6, symbol='circle'),
            # hoverinfo='text',  # émet l’infobulle pour ce point
            # hovertext=['Minima à {:.2f}s'.format(time[i]) for i in cycles[:,1]]
        ))

        if cycles_on_bpm:
            for i in cycles[:, 0]:  # Minima en vert
                fig.add_shape(
                    type='line',
                    x0=time[i], x1=time[i],
                    y0=0, y1=-4,
                    line=dict(color='green', width=1),
                    layer='below'
                )
                print(f"cycles {i} fait", end="\r")
            for i in cycles[:, 1]:  # Maxima en rouge
                fig.add_shape(
                    type='line',
                    x0=time[i], x1=time[i],
                    y0=0, y1=-4,
                    line=dict(color='red', width=1),
                    layer='below'
                )
                print(f"cycles {i} fait", end="\r")
    
    if not(ecg2 is None):
        fig.add_trace(scatter_object(
            x=time,
            y=ecg2,
            mode='lines',
            name="ECG",
            line=dict(color="#FF5900"),
        ))
    
    if not(clean_ecg2 is None):
        fig.add_trace(scatter_object(
            x=time,
            y=clean_ecg2,
            mode='lines',
            name="ECG filtered",
            line=dict(color='red')
        ))
    
    if not(r_spikes is None):
        # Dessine en priorité les points de l'ecg avant nettoyage
        y = clean_ecg2[r_spikes]# ecg2[r_spikes] if not(ecg2 is None) else clean_ecg2[r_spikes]
        fig.add_trace(scatter_object(
            x=time[r_spikes],
            y=y,
            mode='markers',
            name="R-peaks",
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
    if not(bpm is None ) and not(time_bpm is None):
        fig.add_trace(scatter_object(
            x=time_bpm,
            y=bpm,
            mode='lines',
            name='Instant HR',
            line=dict(color="green")
        ))
    
    if not(gsr is None):
        # Courbe originale (bleu)
        fig.add_trace(scatter_object(
            x=time,
            y=gsr,
            mode="lines",
            name="GSR",
            line=dict(color="purple"),
            hoverinfo='skip'
        ))

    # Mise en page
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Time (s)",
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
    to_show = ['Filtered Respiration', 'Instant HR', 'Maxima (start expiration)', 'Minima (start inspiration)']
    for trace in fig.data:
        # Remplacez ces noms par ceux que vous voulez cacher au départ
        if not (trace.name in to_show):
            trace.visible = 'legendonly'
    return fig

def normalised_ecg_resp_plot(time: np.ndarray, resp=None, processed_resp=None,
                             cycles=None, ecg=None, processed_ecg=None,
                             r_spikes=None, status=None, micro=None, is_ds=True,
                             bpm=None, time_bpm=None, gsr=None, cycles_on_bpm=True, title="Signals"):
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
        beta = 8 # if not bpm or not time_bpm else 6
        micro = 2* ((micro - np.min(micro)) / (np.max(micro) - np.min(micro))) - beta
    
    if not(gsr is None):
        beta = 6
        gsr = 2* ((gsr - np.min(gsr)) / (np.max(gsr) - np.min(gsr))) - beta

    if not(bpm is None) and not(time_bpm is None):
        bpm = 2* ((bpm - np.min(bpm)) / (np.max(bpm) - np.min(bpm))) - 4


    return build_fig(time, resp, processed_resp, cycles, 
              ecg, processed_ecg, r_spikes['peak_index'], 
              title=title, status=status, is_ds=is_ds,
              micro=micro, bpm=bpm, time_bpm=time_bpm, gsr=gsr, cycles_on_bpm=cycles_on_bpm)


def plot_instant_asr(
    times: np.ndarray, amps: np.ndarray, max_window=10, feature='RSA', status=None, time=None
) -> go.Figure:
    """
        Déssine une valeur déterminante de la respHRV,
        présente sur chaque cycles
    """
    df = pd.DataFrame({"times": times, "amps": amps})

    # Figure de base : trace des amplitudes
    fig = go.Figure(
        data=[
            go.Scatter(
                x=df["times"],
                y=df["amps"],
                mode="markers+lines",
                name=f"{feature} (respHRV)",
                marker=dict(size=6, opacity=0.6),
            ),
            # Trace de la moyenne mobile initiale (window=1)
            go.Scatter(
                x=df["times"],
                y=df["amps"].rolling(window=1, center=True).mean(),
                mode="lines",
                name="MA",
                line=dict(width=3, color="darkorange"),
            )
        ],
        layout=go.Layout(
            title="respHRV evolution in time (moving average window slider)",
            xaxis_title="Time (s)",
            yaxis_title=f"{feature} (bpm)",
            template="plotly_white",
            sliders=[{
                "active": 0,
                "pad": {"t": 50},
                "currentvalue": {"prefix": "Window size: "},
                "steps": [
                    {
                        "label": str(w),
                        "method": "animate",
                        "args": [
                            [f"frame{w}"],
                            {"mode": "immediate", "frame": {"duration": 0}, "transition": {"duration": 0}}
                        ]
                    }
                    for w in range(1, max_window + 1)
                ]
            }]
        ),
        frames=[
            go.Frame(
                data=[
                    # Les mêmes deux traces, raw et MA(w)
                    go.Scatter(x=df["times"], y=df["amps"]), 
                    go.Scatter(
                        x=df["times"],
                        y=df["amps"].rolling(window=w, center=True).mean()
                    )
                ],
                name=f"frame{w}"
            )
            for w in range(1, max_window + 1)
        ]
    )
    
    if status != None:
        for i in range(len(status[50])):
            label_title = "stress" if (i % 2) != 0 else "rest"
            fig.add_vline(x=time[status[50][i]], annotation_text=f"Start {label_title}", 
                annotation_position="bottom right")
            fig.add_vline(x=time[status[70][i]], annotation_text=f"End {label_title}", 
                annotation_position="bottom left")
    return fig


def plot_mean_asr_by_phase(df, metric: str):
    fig=go.Figure()
    values = df[metric].tolist()
    fig.add_trace(go.Scatter(
        x=('repos1', 'stress', 'repos2'),
        y=values,
        mode="lines",
        name=f"Mean {metric}",
        line=dict(color="purple"),
        hoverinfo='skip'
    ))
    return fig

import plotly.graph_objs as go

def plot_filtering(time, signals, max_freqs, raw_resp):
    """
    Crée une figure Plotly où chaque fréquence est une trace,
    et un slider qui rend visible la trace désirée.
    """
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
            x=time,
            y=raw_resp,
            mode="lines",
            name="Respiration",
            line=dict(color="blue"),
            visible=True,
            hoverinfo='skip'
            # hoverinfo='skip'
    ))
    for i, freq in enumerate(max_freqs):
        fig.add_trace(
            go.Scattergl(
                x = time,
                y = signals[freq],
                mode = 'lines',
                name = f"{freq:.1f} Hz",
                line=dict(color="orange"),
                visible = (i == 0),      # seule la première trace est visible au départ
                hoverinfo='skip'
            )
        )
    

    steps = []
    for i, freq in enumerate(max_freqs):
        step = dict(
            method = "restyle",      
            args = [
                {"visible": [                         # 1ère position = raw_resp
                    True                         # raw_resp visible
                ] + [j == i for j in range(len(max_freqs))]},
                
                {"title": f"Signal à fréquence max = {freq:.1f} Hz"} 
            ],
            label = f"{freq:.1f} Hz"
        )
        steps.append(step)
    
    sliders = [dict(
        active = 0,
        pad = {"t": 30},
        currentvalue = {"prefix": "Fréq max : ", "suffix": " Hz"},
        steps = steps
    )]
    
    fig.update_layout(
        xaxis = dict(title="Temps (s)"),
        yaxis = dict(title="Amplitude"),
        sliders = sliders
    )
    
    return fig


# def gsr_plot(
#     scr_events: pd.DataFrame = None,
#     gsr_raw: pd.Series = None,
#     sampling_rate: float = None,
#     target_fs: float = None
# ):
#     temp = None
#     if gsr_raw is None or sampling_rate is None:
#         temp = config.read_data()
#         gsr_raw = temp["gsr"]
#         sampling_rate = temp["sf"]
#     gsr_raw = pd.Series(gsr_raw)
#     if target_fs is None:
#         if temp is not None and "ds_freq" in temp:
#             target_fs = float(temp["ds_freq"])
#         else:
#             target_fs = 10.0

#     if not isinstance(gsr_raw, pd.Series):
#         raise TypeError("gsr_raw doit être un pandas.Series")
#     sr = float(sampling_rate)
#     if sr <= 0:
#         raise ValueError("sampling_rate doit être > 0")
#     x = gsr_raw.astype(float).copy()
#     if x.isna().any():
#         x = x.interpolate(limit_direction="both")
#     n = len(x)
#     if n == 0:
#         raise ValueError("Signal vide")

#     if scr_events is None or not isinstance(scr_events, pd.DataFrame):
#         raise ValueError("scr_events doit être un DataFrame non vide contenant les pics SCR.")

#     tf = float(target_fs) if target_fs else 10.0
#     if tf <= 0:
#         tf = 10.0

#     t_raw = np.arange(n) / sr
#     num_out = int(round(n * tf / sr))
#     num_out = max(num_out, 2)
#     t_down = np.arange(num_out) / tf
#     # Interpolation linéaire pour avoir gsr_down à t_down
#     # (on interpole la série brute x(t_raw) vers t_down)
#     gsr_down = np.interp(t_down, t_raw, x.values)

#     # --------- Construire les temps absolus des pics (t_peaks, en secondes) ---------
#     cols = set(scr_events.columns)
#     t_peaks = None

#     # On a besoin de status pour convertir les temps relatifs 'phase' -> absolu
#     status_raw = None
#     if temp is not None and isinstance(temp.get("status", None), dict):
#         status_raw = temp["status"]

#     # Cas 1 : temps absolu direct
#     if "t_global_s" in cols:
#         t_peaks = pd.to_numeric(scr_events["t_global_s"], errors="coerce").to_numpy(dtype=float)

#     # Cas 2 : phase + indices/temps relatifs, avec status (indices RAW start/end par phase)
#     elif "phase" in cols and status_raw is not None and (("peak_idx" in cols) or ("t_peak_s" in cols)):
#         t_list = []
#         for _, row in scr_events.iterrows():
#             ph = row["phase"]
#             # clé phase (int/str)
#             ph_key = ph if ph in status_raw else str(ph)
#             if ph_key not in status_raw or not isinstance(status_raw[ph_key], (list, tuple)) or len(status_raw[ph_key]) != 2:
#                 t_list.append(np.nan)
#                 continue
#             start_idx = float(status_raw[ph_key][0])  # index de début au fs brut
#             if "peak_idx" in cols and pd.notna(row.get("peak_idx", np.nan)):
#                 t_list.append((start_idx + float(row["peak_idx"])) / sr)
#             elif "t_peak_s" in cols and pd.notna(row.get("t_peak_s", np.nan)):
#                 t_list.append((start_idx / sr) + float(row["t_peak_s"]))
#             else:
#                 t_list.append(np.nan)
#         t_peaks = np.asarray(t_list, dtype=float)

#     # Cas 3 : indices globaux
#     elif "peak_idx" in cols:
#         t_peaks = pd.to_numeric(scr_events["peak_idx"], errors="coerce").to_numpy(dtype=float) / sr

#     # Cas 4 : t_peak_s supposé absolu (fallback)
#     elif "t_peak_s" in cols:
#         t_peaks = pd.to_numeric(scr_events["t_peak_s"], errors="coerce").to_numpy(dtype=float)

#     else:
#         raise ValueError(
#             "scr_events ne contient pas d'information temporelle exploitable. "
#             "Attendu: 't_global_s' OU ('phase' + ('peak_idx' ou 't_peak_s') avec status) "
#             "OU 'peak_idx' (global) OU 't_peak_s' (absolu)."
#         )

#     # Nettoyage/clip aux bornes du signal
#     t_peaks = np.asarray(t_peaks, dtype=float)
#     valid = np.isfinite(t_peaks) & (t_peaks >= t_raw[0]) & (t_peaks <= t_raw[-1])
#     t_peaks = t_peaks[valid]

#     # Valeur des pics projetée sur le tracé downsamplé (interpolation sur t_down)
#     y_peaks = np.interp(t_peaks, t_down, gsr_down) if t_peaks.size else np.array([])

#     # --------- Figure ----------
#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(
#             x=t_down, y=gsr_down, mode="lines", name="GSR (downsampled)",
#             hovertemplate="t=%{x:.2f}s<br>GSR=%{y:.4f}<extra></extra>",
#         )
#     )
#     if t_peaks.size:
#         fig.add_trace(
#             go.Scatter(
#                 x=t_peaks, y=y_peaks, mode="markers", name="SCR Peaks",
#                 marker=dict(size=8, symbol="x"),
#                 hovertemplate="Peak @ %{x:.2f}s<br>GSR=%{y:.4f}<extra></extra>",
#             )
#         )

#     # --------- Lignes de phase : on REPRODUIT ton workflow (status -> indices downsample -> t_down[idx]) ---------
#     if status_raw is not None and isinstance(status_raw, dict) and len(status_raw) > 0:
#         # Construire une version downsamplée des indices de phase (comme dans ton code d'origine)
#         # idx_ds = round(idx_raw / (sr / tf))
#         status_ds = {}
#         scale = sr / tf
#         for k, bounds in status_raw.items():
#             if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
#                 s_idx = int(round(float(bounds[0]) / scale))
#                 e_idx = int(round(float(bounds[1]) / scale))
#                 # clamp aux bornes de t_down
#                 s_idx = int(np.clip(s_idx, 0, len(t_down) - 1))
#                 e_idx = int(np.clip(e_idx, 0, len(t_down) - 1))
#                 status_ds[k] = [s_idx, e_idx]

#         # Si format "50"/"70" existe on refait exactement ta boucle ; sinon on trace générique
#         if 50 in status_ds and 70 in status_ds:
#             for i in range(len(status_ds[50])):
#                 label_title = "stress" if (i % 2) != 0 else "rest"
#                 fig.add_vline(
#                     x=t_down[status_ds[50][i]],
#                     annotation_text=f"Start {label_title}",
#                     annotation_position="bottom right",
#                 )
#                 fig.add_vline(
#                     x=t_down[status_ds[70][i]],
#                     annotation_text=f"End {label_title}",
#                     annotation_position="bottom left",
#                 )
#         else:
#             # fallback: pour chaque phase clé
#             for key, (s_idx, e_idx) in status_ds.items():
#                 label_title = f"phase {key}"
#                 fig.add_vline(
#                     x=t_down[s_idx],
#                     annotation_text=f"Start {label_title}",
#                     annotation_position="bottom right",
#                 )
#                 fig.add_vline(
#                     x=t_down[e_idx],
#                     annotation_text=f"End {label_title}",
#                     annotation_position="bottom left",
#                 )

#     fig.update_layout(
#         title="GSR downsamplé avec pics SCR (aligné)",
#         xaxis_title="Temps (s)",
#         yaxis_title="Amplitude GSR",
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
#         margin=dict(l=50, r=20, t=60, b=50),
#     )

#     return fig

import neurokit2 as nk

def gsr_plot_with_metrics(
    gsr_raw: pd.Series = None,
    sampling_rate: float = None,
    target_fs: float = None,
):
    """
    Parameters
    ----------
    gsr_raw : pd.Series
        Colonne pandas contenant le signal GSR brut (EDA).
    sampling_rate : float
        Fréquence d'échantillonnage (Hz) du signal gsr_raw.
    target_fs : float, optional
        Fréquence d'échantillonnage (Hz) à utiliser pour l'affichage (downsampling), par défaut 10 Hz.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Figure Plotly avec le GSR downsamplé et les pics SCR marqués.
    metrics : pd.DataFrame
        Métriques EDA/SCR calculées par neurokit2 (interval-related).
    """
    # On lit les données saved si pas de gsr renseignée
    temp = config.read_data()
    if gsr_raw is None or sampling_rate is None:
        gsr_raw = temp["gsr"]
        print("\n\n\n\n\n\n", type(temp["ds_freq"]))
        sampling_rate = temp["sf"]
    gsr_raw = pd.Series(gsr_raw)
    if target_fs == None:
        target_fs = temp["ds_freq"]

    status = temp["status"]
    status[50] = [int(v / (sampling_rate/target_fs)) for v in status[50]]
    status[70] = [int(v / (sampling_rate/target_fs)) for v in status[70]]
    # --- Sécurité d'entrée ---

    if not isinstance(gsr_raw, pd.Series):
        raise TypeError("gsr_raw doit être un pandas.Series")
    sr = int(round(float(sampling_rate)))
    if sr <= 0:
        raise ValueError("sampling_rate doit être > 0")
    x = gsr_raw.astype(float).copy()
    if x.isna().any():
        x = x.interpolate(limit_direction="both")
    n = len(x)
    if n == 0:
        raise ValueError("Signal vide")

    # ---------- Pipeline NeuroKit2 (officiel) ----------
    # Donne les colonnes: EDA_Raw, EDA_Clean, EDA_Tonic, EDA_Phasic, SCR_Onsets, SCR_Peaks, SCR_Amplitude, etc.
    signals, info = nk.eda_process(x.values, sampling_rate=sr)  # :contentReference[oaicite:0]{index=0}

    # ---------- Métriques interval-related (NeuroKit2) ----------
    # eda_intervalrelated calcule: SCR_Peaks_N, SCR_Peaks_Amplitude_Mean, EDA_Tonic_SD
    # + EDA_Sympathetic si durée > 64 s, + EDA_Autocorrelation si durée > 30 s
    # On garde un fallback solide pour tolérer des versions anciennes/buguées.
    try:
        metrics = nk.eda_intervalrelated(signals, sampling_rate=sr)  # :contentReference[oaicite:1]{index=1}
        # normalise la sortie (une seule ligne)
        metrics = metrics.reset_index(drop=True)
    except Exception:
        data = {}
        cols = signals.columns

        # Nombre de pics SCR
        if "SCR_Peaks" in cols:
            data["SCR_Peaks_N"] = np.nansum(signals["SCR_Peaks"].values)
        else:
            data["SCR_Peaks_N"] = np.nan

        # Amplitude moyenne des pics (sur les échantillons marqués 1)
        if "SCR_Amplitude" in cols and "SCR_Peaks" in cols:
            pk = signals["SCR_Peaks"].values.astype(bool)
            data["SCR_Peaks_Amplitude_Mean"] = (
                float(np.nanmean(signals.loc[pk, "SCR_Amplitude"].values)) if pk.any() else np.nan
            )
        else:
            data["SCR_Peaks_Amplitude_Mean"] = np.nan

        # Variabilité du tonique (SD)
        data["EDA_Tonic_SD"] = float(np.nanstd(signals["EDA_Tonic"].values)) if "EDA_Tonic" in cols else np.nan

        # EDA_Sympathetic (si durée suffisante)
        data.update({"EDA_Sympathetic": np.nan, "EDA_SympatheticN": np.nan})
        if n > sr * 64:
            src = "EDA_Clean" if "EDA_Clean" in cols else ("EDA_Raw" if "EDA_Raw" in cols else None)
            if src is not None:
                try:
                    data.update(nk.eda_sympathetic(signals[src], sampling_rate=sr))
                except Exception:
                    pass

        # Autocorrélation (si durée suffisante) — lag=4 s (par défaut dans la doc)
        data["EDA_Autocorrelation"] = np.nan
        if n > sr * 30:
            src = "EDA_Clean" if "EDA_Clean" in cols else ("EDA_Raw" if "EDA_Raw" in cols else None)
            if src is not None:
                try:
                    data["EDA_Autocorrelation"] = float(nk.eda_autocor(signals[src], sampling_rate=sr, lag=4))
                except Exception:
                    pass

        metrics = pd.DataFrame([data])

    # ---------- Pics SCR (indices -> temps) ----------
    if "SCR_Peaks" in signals.columns:
        scr_peaks_idx = np.where(signals["SCR_Peaks"].values == 1)[0]
    else:
        scr_peaks_idx = np.array([], dtype=int)
    t_peaks = scr_peaks_idx / float(sr)

    # ---------- Downsample du BRUT pour l'affichage ----------
    tf = int(round(float(target_fs))) if target_fs is not None else 10
    if tf <= 0:
        tf = 10
    # signal_resample RENVOIE UNIQUEMENT le vecteur resamplé (pas (y, t) !)
    gsr_down = nk.signal_resample(
        x.values, sampling_rate=sr, desired_sampling_rate=tf, method="interpolation"
    )  # :contentReference[oaicite:2]{index=2}
    t_down = np.arange(len(gsr_down)) / float(tf)

    # Valeur des pics projetée sur le tracé downsamplé (interpolation temporelle)
    y_peaks = np.interp(t_peaks, t_down, gsr_down) if t_peaks.size else np.array([])

    # ---------- Plotly (retourne la figure, sans show) ----------
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=t_down,
            y=gsr_down,
            mode="lines",
            name="GSR (downsampled)",
            hovertemplate="t=%{x:.2f}s<br>GSR=%{y:.4f}<extra></extra>",
        )
    )
    if t_peaks.size:
        fig.add_trace(
            go.Scatter(
                x=t_peaks,
                y=y_peaks,
                mode="markers",
                name="SCR Peaks",
                marker=dict(size=8, symbol="x"),
                hovertemplate="Peak @ %{x:.2f}s<br>GSR=%{y:.4f}<extra></extra>",
            )
        )

    for i in range(len(status[50])):
            label_title = "stress" if (i % 2) != 0 else "rest"
            fig.add_vline(x=t_down[status[50][i]], annotation_text=f"Start {label_title}", 
                annotation_position="bottom right")
            fig.add_vline(x=t_down[status[70][i]], annotation_text=f"End {label_title}", 
                annotation_position="bottom left")

    fig.update_layout(
        title="GSR downsamplé avec pics SCR",
        xaxis_title="Temps (s)",
        yaxis_title="Amplitude GSR",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=50, r=20, t=60, b=50),
    )

    return fig, metrics