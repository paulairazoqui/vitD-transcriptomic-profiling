# src/vitd_utils/dataset.py
from __future__ import annotations
from typing import Iterable, Optional, Tuple
import pandas as pd

__all__ = [
    "standardize_meta", 
    "align_exp_meta", 
    "effects_by_cell",
    "build_core_scores_df"
    ]

def _pick_first(cols: Iterable[str], candidates) -> Optional[str]:
    cols_set = set(cols)
    for c in candidates:
        if c in cols_set:
            return c
    return None

def standardize_meta(meta: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize metadata columns:
      - 'sig_id'   from: sig_id | signature_id | sig
      - 'cell_id'  from: cell_id | cell
      - 'dose'     from: dose | pert_dose | pert_idose | x_dose
      - 'analog'   from: cmap_name | pert_iname | pert_desc | pert_name | compound | drug (optional)
    Coerces 'dose' to numeric if present.
    """
    if not isinstance(meta, pd.DataFrame):
        raise TypeError("meta must be a pandas DataFrame")

    meta = meta.copy()
    meta.columns = meta.columns.str.strip()  # <— elimina espacios accidentales

    cols = meta.columns

    cols = meta.columns
    sig_col    = _pick_first(cols, ["sig_id", "signature_id", "sig"])
    cell_col   = _pick_first(cols, ["cell_id", "cell"])
    dose_col   = _pick_first(cols, ["dose", "pert_dose", "pert_idose", "x_dose"])
    analog_col = _pick_first(cols, ["cmap_name", "pert_iname", "pert_desc", "pert_name", "compound", "drug"])

    if sig_col is None or cell_col is None:
        raise ValueError(f"Metadata is missing required columns. Found: {list(cols)}")

    rename_map = {}
    if sig_col   != "sig_id":   rename_map[sig_col]   = "sig_id"
    if cell_col  != "cell_id":  rename_map[cell_col]  = "cell_id"
    if dose_col  and dose_col != "dose":   rename_map[dose_col]  = "dose"
    if analog_col and analog_col != "analog": rename_map[analog_col] = "analog"

    out = meta.copy()
    if rename_map:
        out = out.rename(columns=rename_map)

    if "dose" in out.columns:
        out["dose"] = pd.to_numeric(out["dose"], errors="coerce")

    return out

def align_exp_meta(exp: pd.DataFrame, meta: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Align expression (genes×signatures) and metadata on 'sig_id'."""
    if "sig_id" not in meta.columns:
        raise ValueError("meta must contain 'sig_id' (run standardize_meta first).")
    sigs = set(meta["sig_id"])
    keep = [c for c in exp.columns if c in sigs]
    exp2 = exp[keep].copy()
    meta2 = meta.loc[meta["sig_id"].isin(keep)].copy()
    return exp2, meta2

def effects_by_cell(exp: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """Build gene×cell effects by averaging signatures within each cell line."""
    if not {"sig_id", "cell_id"}.issubset(meta.columns):
        raise ValueError("meta must contain 'sig_id' and 'cell_id'.")
    indexer = meta.set_index("sig_id")["cell_id"]
    return exp.T.groupby(indexer).mean().T


# --- Build core_scores_df (sig_id, cell_id, log_dose, core_score) ------------
import pandas as pd
import numpy as np
from typing import Union

def build_core_scores_df(
    sig_meta: pd.DataFrame,
    core_scores: Union[pd.Series, pd.DataFrame],
    id_col: str = "sig_id",
    cell_col: str = "cell_id",
    dose_col: str = "log_dose",
    score_col: str = "core_score",
) -> pd.DataFrame:
    """
    Merge signature metadata with core scores to produce a tidy table for analysis.

    Parameters
    ----------
    sig_meta : DataFrame
        Must contain signature IDs and cell labels. Expected columns:
        - id_col (default 'sig_id')
        - cell_col (default 'cell_id')
        - dose_col (default 'log_dose'). If missing, tries to compute from 'dose'.
    core_scores : Series or DataFrame
        If Series: index should be sig_id; values are the core scores.
        If DataFrame: should include [id_col, score_col] or have score_col detectable.
    id_col, cell_col, dose_col, score_col : str
        Column names to use.

    Returns
    -------
    DataFrame
        Columns: [sig_id, cell_id, log_dose, core_score]; rows with NaN dropped.
    """
    if not isinstance(sig_meta, pd.DataFrame):
        raise ValueError("sig_meta must be a DataFrame.")

    meta = sig_meta.copy()

    # Normalize dose column
    if dose_col not in meta.columns:
        if "log10_dose" in meta.columns:
            meta = meta.rename(columns={"log10_dose": dose_col})
        elif "dose" in meta.columns and pd.api.types.is_numeric_dtype(meta["dose"]):
            meta[dose_col] = np.log10(meta["dose"].replace(0, np.nan))
        else:
            raise ValueError(f"Metadata missing '{dose_col}' and no numeric 'dose' to derive it.")

    # Normalize ID column
    if id_col not in meta.columns:
        # try some common alternatives
        for alt in ("signature_id", "sig", "id"):
            if alt in meta.columns:
                meta = meta.rename(columns={alt: id_col})
                break
    if id_col not in meta.columns:
        raise ValueError(f"Metadata missing '{id_col}'.")

    # Prepare scores
    if isinstance(core_scores, pd.Series):
        scores_df = core_scores.rename(score_col).reset_index()
        # name of index becomes id_col if set, else assume first column
        if scores_df.columns[0] != id_col:
            scores_df = scores_df.rename(columns={scores_df.columns[0]: id_col})
    elif isinstance(core_scores, pd.DataFrame):
        s = core_scores.copy()
        if score_col not in s.columns:
            # attempt to detect a score column
            candidates = [c for c in s.columns if c.lower() in {"core_score", "score", "corescore"}]
            if not candidates:
                raise ValueError("Could not find a core score column in core_scores DataFrame.")
            s = s.rename(columns={candidates[0]: score_col})
        if id_col not in s.columns:
            if s.index.name:
                s = s.reset_index().rename(columns={s.index.name: id_col})
            else:
                raise ValueError(f"core_scores DataFrame lacks '{id_col}' and unnamed index.")
        scores_df = s[[id_col, score_col]]
    else:
        raise ValueError("core_scores must be a Series or DataFrame.")

    out = (meta.merge(scores_df, on=id_col, how="inner")
                [[id_col, cell_col, dose_col, score_col]]
                .dropna())
    out.columns = ["sig_id", "cell_id", "log_dose", "core_score"]  # estandarizamos
    return out
