# src/vitd_utils/idsymbols.py
"""
ID ↔ symbol utilities for the Vitamin D transcriptomic profiling project.

This module centralizes small helpers to:
- Build a robust gene_id → gene_symbol mapping from heterogeneous metadata.
- Map any iterable of gene_ids to symbols, with safe fallbacks.

Design goals
------------
- Be tolerant to missing/empty columns and duplicated rows.
- Never crash if symbols are partially missing: fall back to the gene_id.
- Return plain Python types that are easy to use in notebooks (pd.Series, list[str]).

Examples
--------
>>> import pandas as pd
>>> from vitd_utils.idsymbols import build_symbol_map, map_symbols_or_ids
>>> gi = pd.DataFrame({
...     "gene_id":  ["100", "101", "102", "103", "104"],
...     "gene_symbol": ["DDIT4", "IGFBP3", None, "NPC1", ""],
... })
>>> sym_map = build_symbol_map(gi)      # index: "100","101",...
>>> map_symbols_or_ids(["100","102","999"], sym_map)
['DDIT4', '102', '999']                  # 102/999 fall back to their IDs
"""

from __future__ import annotations

from typing import Iterable, List, Sequence
import pandas as pd


__all__ = [
    "to_str_index",
    "build_symbol_map",
    "map_symbols_or_ids",
]


def to_str_index(idx_like: Iterable) -> pd.Index:
    """
    Convert any index-like object (list/array/Index) to a pandas Index of strings.

    Parameters
    ----------
    idx_like : Iterable
        Values to convert.

    Returns
    -------
    pd.Index
        String index, safe to use as labels/keys.
    """
    # Pandas handles None/NaN gracefully when cast to string dtype
    return pd.Index(idx_like).astype(str)


def build_symbol_map(
    gene_info: pd.DataFrame,
    symbol_cols: Sequence[str] = ("gene_symbol", "pr_gene_symbol", "symbol"),
    id_col: str = "gene_id",
) -> pd.Series:
    """
    Build a Series mapping gene_id (string) → gene_symbol (may contain NaN).

    The function is robust to varying schemas: it picks the *first* available
    column from `symbol_cols`. Duplicated `gene_id` rows are de-duplicated
    keeping the first occurrence.

    Parameters
    ----------
    gene_info : pd.DataFrame
        Gene metadata table that includes at least `id_col` and one of `symbol_cols`.
    symbol_cols : Sequence[str], default ("gene_symbol","pr_gene_symbol","symbol")
        Candidate columns that may contain the official gene symbol.
    id_col : str, default "gene_id"
        Column with the stable gene identifier used throughout the project.

    Returns
    -------
    pd.Series
        Index = gene_id (str), values = gene_symbol (object).
        If no valid symbol column exists, returns an empty Series (dtype=object).

    Notes
    -----
    - Symbols are **not** auto-imputed here; fallback is handled by `map_symbols_or_ids`.
    - The returned Series can be used with `.reindex()` safely.
    """
    if not isinstance(gene_info, pd.DataFrame):
        return pd.Series(dtype=object)

    # Pick the first available symbol column
    sym_col = next((c for c in symbol_cols if c in gene_info.columns), None)
    if sym_col is None or id_col not in gene_info.columns:
        return pd.Series(dtype=object)

    gi = gene_info[[id_col, sym_col]].drop_duplicates(subset=[id_col]).copy()
    gi[id_col] = gi[id_col].astype(str)

    # Normalize obvious “empty” strings to NaN for consistency
    vals = pd.Series(gi[sym_col], copy=True)
    mask_empty = (
        vals.isna()
        | (vals.astype(str).str.strip() == "")
        | (vals.astype(str).str.lower().isin(["nan", "none"]))
    )
    vals.loc[mask_empty] = pd.NA

    series = vals.set_axis(gi[id_col].astype(str)).copy()
    series.index.name = id_col
    return series


def map_symbols_or_ids(ids: Iterable, sym_map: pd.Series) -> List[str]:
    """
    Map an iterable of gene_ids to gene symbols with a safe fallback to the id.

    Parameters
    ----------
    ids : Iterable
        Any iterable of identifiers. Values will be coerced to strings.
    sym_map : pd.Series
        Output of `build_symbol_map`. The index must be gene_id (str).

    Returns
    -------
    list[str]
        A list of symbols where available; otherwise the original id (as string).

    Behavior
    --------
    - If `sym_map` is empty or missing values, those positions fall back to the id.
    - Leading/trailing spaces and "nan"/"none" strings are treated as missing.
    - The output length always matches the input length.

    Examples
    --------
    >>> sym_map = pd.Series({"100":"DDIT4","101":"IGFBP3"})
    >>> map_symbols_or_ids(["100","102"], sym_map)
    ['DDIT4', '102']
    """
    ids_str = to_str_index(ids)

    if isinstance(sym_map, pd.Series) and not sym_map.empty:
        lookup = sym_map.reindex(ids_str).astype(object)
    else:
        lookup = pd.Series(index=ids_str, dtype=object)

    # Identify missing/blank/placeholder symbols and replace with the id itself
    na_mask = (
        lookup.isna()
        | (lookup.astype(str).str.strip() == "")
        | (lookup.astype(str).str.lower().isin(["nan", "none"]))
    )
    lookup.loc[na_mask] = ids_str[na_mask]
    return lookup.astype(str).tolist()
