# src/vitd_utils/stats.py
"""
Statistical helpers for the Vitamin D transcriptomic profiling project.

This module provides small, dependency-light utilities used across notebooks:
- spearman_by_group: groupwise Spearman correlation (rho, p-value, n).
- add_fdr: Benjamini–Hochberg FDR correction for a DataFrame column.
- bootstrap_ci: nonparametric bootstrap confidence interval for the median.
- fit_slope_ols: quick OLS slope via numpy polyfit (y ~ x).

Design goals
------------
- Minimal external dependencies (only numpy/pandas/scipy/statsmodels where needed).
- Safe defaults (filters for tiny groups, coercion to numeric).
- Return tidy pandas DataFrames ready for presentation/plotting.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence
import numpy as np
import pandas as pd
from scipy import stats as spstats
from statsmodels.stats.multitest import multipletests


__all__ = [
    "spearman_by_group",
    "add_fdr",
    "bootstrap_ci",
    "fit_slope_ols",
]


def spearman_by_group(
    df: pd.DataFrame,
    group_cols: str | Sequence[str],
    x: str,
    y: str,
    min_n: int = 4,
    min_unique: int = 2,
    dropna: bool = True,
) -> pd.DataFrame:
    """
    Compute Spearman correlation (rho, p-value) per group.

    Parameters
    ----------
    df : pd.DataFrame
        Input table containing x, y and grouping columns.
    group_cols : str | Sequence[str]
        Column(s) to group by (e.g., "cell_id", ["cmap_name","cell_id"]).
    x, y : str
        Column names to correlate (e.g., "log_dose", "core_score").
    min_n : int, default 4
        Minimum group size to compute correlation.
    min_unique : int, default 2
        Minimum number of unique x-values required (avoid degenerate cases).
    dropna : bool, default True
        Drop rows with NaN in x or y before grouping.

    Returns
    -------
    pd.DataFrame
        Columns: group_cols..., n, rho, pval
    """
    if isinstance(group_cols, str):
        group_cols = [group_cols]

    work = df[[*group_cols, x, y]].copy()
    if dropna:
        work = work.dropna(subset=[x, y])

    rows: List[dict] = []
    for keys, sub in work.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        n = len(sub)
        if n < min_n:
            continue
        if sub[x].nunique(dropna=True) < min_unique:
            continue
        rho, pval = spstats.spearmanr(sub[x].values, sub[y].values)
        rec = {c: k for c, k in zip(group_cols, keys)}
        rec.update({"n": int(n), "rho": float(rho), "pval": float(pval)})
        rows.append(rec)

    return pd.DataFrame(rows)


def add_fdr(df: pd.DataFrame, p_col: str = "pval", out_col: str = "fdr_bh") -> pd.DataFrame:
    """
    Add a Benjamini–Hochberg FDR column to a DataFrame with p-values.

    Parameters
    ----------
    df : pd.DataFrame
        Table containing a p-value column.
    p_col : str, default "pval"
        Name of the p-value column.
    out_col : str, default "fdr_bh"
        Name of the output FDR-adjusted p-value column.

    Returns
    -------
    pd.DataFrame
        Same object with an added FDR column. If df is empty or p_col missing,
        the function returns df unchanged.
    """
    if df is None or len(df) == 0 or p_col not in df.columns:
        return df
    try:
        fdr = multipletests(df[p_col].astype(float).values, method="fdr_bh")[1]
    except Exception:
        # Be conservative in case of bad inputs
        fdr = np.full(len(df), np.nan, dtype=float)
    df[out_col] = fdr
    return df


def bootstrap_ci(
    values: Iterable[float],
    B: int = 4000,
    alpha: float = 0.05,
    random_state: int = 0,
) -> tuple[float, float]:
    """
    Nonparametric bootstrap confidence interval for the median.

    Parameters
    ----------
    values : Iterable[float]
        Numeric vector.
    B : int, default 4000
        Number of bootstrap resamples.
    alpha : float, default 0.05
        Significance level (1 - alpha is the confidence level).
    random_state : int, default 0
        RNG seed for reproducibility.

    Returns
    -------
    (lo, hi) : tuple[float, float]
        Percentile CI bounds. If input has length 0, returns (nan, nan).
        If length 1, returns (value, value).
    """
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return np.nan, np.nan
    if arr.size == 1:
        v = float(arr[0])
        return v, v

    rng = np.random.RandomState(random_state)
    boots = np.empty(B, dtype=float)
    n = arr.size
    for i in range(B):
        boots[i] = np.median(rng.choice(arr, size=n, replace=True))
    lo, hi = np.percentile(boots, [100 * alpha / 2.0, 100 * (1 - alpha / 2.0)])
    return float(lo), float(hi)


def fit_slope_ols(
    df: pd.DataFrame,
    x: str = "log_dose",
    y: str = "core_score",
    require_unique: int = 2,
) -> float:
    """
    Quick OLS slope for y ~ x using numpy polyfit (degree=1).

    Parameters
    ----------
    df : pd.DataFrame
        Data with columns x and y.
    x, y : str
        Column names.
    require_unique : int, default 2
        Minimum number of unique x-values to attempt a fit.

    Returns
    -------
    float
        Estimated slope (Δy per Δx). Returns np.nan if fit is not feasible.

    Notes
    -----
    - For inference (SE/CI/p), use the HC3 robust OLS in `dose.py`.
    - This helper is intended for quick effect-size summaries (no SEs).
    """
    sub = df[[x, y]].dropna()
    if sub[x].nunique() < require_unique or len(sub) < 2:
        return float("nan")
    try:
        slope = float(np.polyfit(sub[x].astype(float).values, sub[y].astype(float).values, 1)[0])
    except Exception:
        slope = float("nan")
    return slope
