# src/vitd_utils/dataset.py
from __future__ import annotations
from typing import Iterable, Optional, Tuple
import pandas as pd

__all__ = ["standardize_meta", "align_exp_meta", "effects_by_cell"]

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
