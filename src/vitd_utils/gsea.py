# src/vitd_utils/gsea.py
from __future__ import annotations
import numpy as np, pandas as pd, json, time, hashlib
from pathlib import Path
from statsmodels.stats.multitest import multipletests

def make_preranked(series: pd.Series, sym_map: pd.Series) -> pd.DataFrame:
    s = pd.to_numeric(series, errors="coerce")
    s.index = s.index.astype(str)
    symbols = pd.Series(
        map_symbols_or_ids(s.index, sym_map), index=s.index, dtype=object
    )
    df = pd.DataFrame({"gene": symbols.values, "score": s.values}, index=s.index)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["score"])
    order = df["score"].abs().sort_values(ascending=False).index
    df = df.loc[order].drop_duplicates(subset="gene", keep="first")
    return df.sort_values("score", ascending=False).reset_index(drop=True)

def load_gmt(path: str | Path) -> dict[str, set[str]]:
    gs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                gs[parts[0]] = set(g for g in parts[2:] if g)
    return gs


