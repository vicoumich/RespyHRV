
import math
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import neurokit2 as nk


PHASES_DEFAULT = ("repos1", "stress", "repos2")

def build_phase_windows(markers: Dict[int, List[int]],
                        n_samples: int,
                        phase_names: Tuple[str, str, str] = PHASES_DEFAULT
                       ) -> List[Tuple[str, int, int]]:
    starts = sorted(markers.get(50, []))
    ends   = sorted(markers.get(70, []))
    if len(starts) != len(ends):
        raise ValueError(f"Nb débuts ({len(starts)}) != fins ({len(ends)}). markers={markers}")
    if len(starts) != len(phase_names):
        raise ValueError(f"On attend {len(phase_names)} phases mais markers en fournit {len(starts)}.")

    windows = []
    for i, ph in enumerate(phase_names):
        s, e = int(starts[i]), int(ends[i])
        s = max(0, min(n_samples-1, s))
        e = max(1, min(n_samples, e))
        if not (s < e):
            raise ValueError(f"Fenêtre invalide pour {ph}: ({s}, {e})")
        windows.append((ph, s, e))
    return windows


def _nk_cols(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    def pick(cands):
        for c in cands:
            if c in df.columns: return c
        return None
    return dict(
        peaks=pick(["SCR_Peaks", "EDA_Peaks"]),
        onsets=pick(["SCR_Onsets", "EDA_Onsets"]),
        recovery=pick(["SCR_Recovery", "EDA_Recovery", "SCR_Recovery_Onsets"]),
        amp=pick(["SCR_Amplitude", "EDA_Amplitude"]),
        clean=pick(["EDA_Clean", "EDA_Filtered", "EDA_Smooth"]),
    )


def _extract_scr_events(signals: pd.DataFrame, fs: float) -> pd.DataFrame:
    cols = _nk_cols(signals)
    if cols["peaks"] is None:
        raise RuntimeError("Colonne des pics SCR introuvable dans les sorties NeuroKit2.")
    peak_idx = np.where(signals[cols["peaks"]].to_numpy().astype(int) == 1)[0]
    on_idx = np.where(signals[cols["onsets"]].to_numpy().astype(int) == 1)[0] if cols["onsets"] else np.array([], int)
    rc_idx = np.where(signals[cols["recovery"]].to_numpy().astype(int) == 1)[0] if cols["recovery"] else np.array([], int)
    amp_arr = signals[cols["amp"]].to_numpy() if cols["amp"] else None

    rows = []
    for k, p in enumerate(peak_idx):
        onset = on_idx[on_idx <= p][-1] if on_idx.size and on_idx[on_idx <= p].size else np.nan
        reco = rc_idx[rc_idx >= p][0] if rc_idx.size and rc_idx[rc_idx >= p].size else np.nan
        ipi = np.nan if k == 0 else (p - peak_idx[k-1]) / fs
        rise = (p - onset) / fs if not np.isnan(onset) else np.nan
        rec_t = (reco - p) / fs if not np.isnan(reco) else np.nan
        amp = float(amp_arr[p]) if amp_arr is not None else np.nan
        rows.append(dict(onset_idx=onset, peak_idx=p, recovery_idx=reco,
                         t_peak_s=p/fs, rise_time_s=rise, recovery_time_s=rec_t,
                         ipi_s=ipi, amplitude=amp))
    return pd.DataFrame(rows)


def _filter_scr_events(events: pd.DataFrame,
                       min_rise_s: float = 0.3,
                       max_rise_s: float = 4.0,
                       min_ipi_s: float = 1.0,
                       min_amp: float = -math.inf,
                       max_recovery_s: float | None = None) -> pd.Series:
    keep = pd.Series(True, index=events.index)
    if "rise_time_s" in events:
        keep &= events["rise_time_s"].between(min_rise_s, max_rise_s, inclusive="both") | events["rise_time_s"].isna()
    if "ipi_s" in events:
        keep &= events["ipi_s"].isna() | (events["ipi_s"] >= min_ipi_s)
    if "amplitude" in events and np.isfinite(events["amplitude"]).any():
        keep &= events["amplitude"] >= min_amp
    if max_recovery_s is not None and "recovery_time_s" in events:
        keep &= events["recovery_time_s"].isna() | (events["recovery_time_s"] <= max_recovery_s)
    return keep

## ADDED ##
# def _scl_metrics(signal):
    
###########

def _scr_metrics(kept: pd.DataFrame) -> Dict[str, float]:
    if kept.shape[0] == 0:
        return dict(n_scr_kept=0, scr_amp_mean=np.nan, scr_amp_median=np.nan,
                    scr_amp_sum=np.nan, rise_time_mean=np.nan, rise_time_median=np.nan)
    return dict(
        n_scr_kept=int(kept.shape[0]),
        scr_amp_mean=float(np.nanmean(kept["amplitude"])),
        scr_amp_median=float(np.nanmedian(kept["amplitude"])),
        scr_amp_sum=float(np.nansum(kept["amplitude"])),
        rise_time_mean=float(np.nanmean(kept["rise_time_s"])),
        rise_time_median=float(np.nanmedian(kept["rise_time_s"])),
    )


def compute_scr_by_phase_for_session(subject: str,
                                     session_id: int,
                                     gsr: np.ndarray,
                                     fs: float,
                                     windows: Dict[int, List[int]],
                                     min_rise_s: float = 0.3,
                                     max_rise_s: float = 4.0,
                                     min_ipi_s: float = 1.0,
                                     min_amp: float = -math.inf,
                                     max_recovery_s: float | None = None):
    """
    Retourne:
      - scr_metrics_df (phase-level)
      - payload_by_phase: dict phase -> {"signals": DataFrame NK (complet),
                                         "events_all": DataFrame,
                                         "events_kept": DataFrame}
    """
    rows = []
    payload = {}
    windows = build_phase_windows(windows, gsr.size)
    for phase, s, e in windows:
        seg = gsr[s:e]
        signals, info = nk.eda_process(seg, sampling_rate=fs) 
        events = _extract_scr_events(signals, fs=fs)
        keep = _filter_scr_events(events, min_rise_s, max_rise_s, min_ipi_s, min_amp, max_recovery_s)
        kept = events[keep].copy()

        row = dict(subject=subject, session_id=session_id, phase=phase,
                   n_scr_raw=int(events.shape[0]), **_scr_metrics(kept))
        rows.append(row)
        payload[phase] = dict(signals=signals, events_all=events, events_kept=kept)

    scr_metrics_df = pd.DataFrame(rows).sort_values(["subject", "session_id", "phase"]).reset_index(drop=True)
    return scr_metrics_df, payload

def compute_scr_with_status(
    gsr: np.ndarray,
    fs: float,
    status: Dict[int, List[int]],
    subject: str = "subj",
    session_id: int = 0,
    min_rise_s: float = 0.3,
    max_rise_s: float = 4.0,
    min_ipi_s: float = 1.0,
    min_amp: float = -math.inf,
    max_recovery_s: float | None = None,
):
    """
    Calcule les métriques SCR et concatène les événements filtrés.

    Paramètres
    ----------
    gsr : np.ndarray
        Signal GSR complet.
    fs : float
        Fréquence d'échantillonnage (Hz).
    status : Dict[int, List[int]]
        Dictionnaire {phase: [start_idx, end_idx]}.
    subject : str
        Identifiant sujet.
    session_id : int
        Identifiant session.

    Retourne
    --------
    scr_metrics_df : pd.DataFrame
        Tableau des métriques agrégées par phase.
    events_all_kept_df : pd.DataFrame
        Tableau concaténé de tous les événements filtrés, avec colonne "phase".
    """
    # Construire la liste de fenêtres comme attendue par compute_scr_by_phase_for_session
    # windows = [(str(phase), bounds[0], bounds[1]) for phase, bounds in status.items()]

    scr_metrics_df, payload = compute_scr_by_phase_for_session(
        subject=subject,
        session_id=session_id,
        gsr=gsr,
        fs=fs,
        windows=status,
        min_rise_s=min_rise_s,
        max_rise_s=max_rise_s,
        min_ipi_s=min_ipi_s,
        min_amp=min_amp,
        max_recovery_s=max_recovery_s,
    )

    # Concaténer tous les events_kept avec ajout de la phase
    events_all_kept = []
    for phase, data in payload.items():
        kept = data["events_kept"].copy()
        kept["phase"] = phase
        events_all_kept.append(kept)

    events_all_kept_df = pd.concat(events_all_kept, ignore_index=True)

    return scr_metrics_df, events_all_kept_df