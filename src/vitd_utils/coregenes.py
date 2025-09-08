# src/vitd_utils/coregenes.py
"""
Consensus 'core' gene logic and core_score computation.

This module implements:
1) Top/bottom ranking per column (e.g., per cell line or analog).
2) Vote-count aggregation across columns to find consensus UP/DOWN genes.
3) Selection of core gene sets (UP/DN) with size/threshold controls.
4) Core score computation for signatures or matrices:
   core_score = mean(z(core_UP)) - mean(z(core_DN))

Inputs are deliberately simple:
- Gene-by-context matrix (index = gene_id or symbol; columns = contexts),
  with numeric effects (e.g., mean z-scores, log FC, signed statistics).
- You can pass either gene IDs or symbols; downstream plotting can map symbols.

Design goals
------------
- Pure functions that return DataFrames/lists (no I/O).
- Deterministic behavior (no RNG).
- Conservative fallbacks when targets cannot be met exactly.

Author: Paula Irazoqui
Project: Vitamin D Transcriptomic Profiling (LINCS L1000)
"""

from __future__ import annotations
from typing import Iterable, List, Tuple, Dict, Optional
import numpy as np
import pandas as pd

from . import config

__all__ = [
    "top_bottom_by_column",
    "vote_counts",
    "pick_core_ids",
    "build_consensus_core",
    "core_score_from_vector",
    "core_score_for_matrix",
]


# ---------------------------------------------------------------------
# 1) Per-column ranking helpers
# ---------------------------------------------------------------------
def top_bottom_by_column(
    effects: pd.DataFrame,
    top_n: int = config.N_TOP,
    min_non_na: int = 10,
) -> Dict[str, Dict[str, List[str]]]:
    """
    For each column, take the top_n most positive (UP) and most negative (DOWN) genes.

    Parameters
    ----------
    effects : pd.DataFrame
        Gene-by-context matrix. Index = genes, columns = contexts (e.g., cell lines).
    top_n : int
        Window size for each extreme.
    min_non_na : int
        Require at least this many non-NaN values in a column to consider it.

    Returns
    -------
    dict
        { column: {"UP": [genes], "DOWN": [genes]} }
        Genes are returned as index labels (strings if index is string-like).

    Notes
    -----
    - Ties follow pandas/numpy stable sort; we keep first encountered order.
    - Columns failing the non-NaN threshold are skipped.
    """
    out: Dict[str, Dict[str, List[str]]] = {}
    for col in effects.columns:
        s = pd.to_numeric(effects[col], errors="coerce").dropna()
        if len(s) < min_non_na:
            continue
        s_sorted = s.sort_values(ascending=False)
        up = s_sorted.head(top_n).index.tolist()
        dn = s_sorted.tail(top_n).index.tolist()  # most negative at the tail
        out[col] = {"UP": up, "DOWN": dn}
    return out


# ---------------------------------------------------------------------
# 2) Vote-count across columns
# ---------------------------------------------------------------------
def vote_counts(
    extremes_by_col: Dict[str, Dict[str, List[str]]]
) -> Tuple[pd.Series, pd.Series]:
    """
    Aggregate vote counts across columns for UP and DOWN sets.

    Parameters
    ----------
    extremes_by_col : dict
        Output of top_bottom_by_column().

    Returns
    -------
    (votes_up, votes_dn) : (pd.Series, pd.Series)
        Index = genes; values = vote counts (int), sorted descending.
    """
    up_votes: Dict[str, int] = {}
    dn_votes: Dict[str, int] = {}

    for col, d in extremes_by_col.items():
        for g in d.get("UP", []):
            up_votes[g] = up_votes.get(g, 0) + 1
        for g in d.get("DOWN", []):
            dn_votes[g] = dn_votes.get(g, 0) + 1

    votes_up = pd.Series(up_votes, dtype=int).sort_values(ascending=False)
    votes_dn = pd.Series(dn_votes, dtype=int).sort_values(ascending=False)
    return votes_up, votes_dn


# ---------------------------------------------------------------------
# 3) Core selection with targets and thresholds
# ---------------------------------------------------------------------
def _tie_break_scores(
    effects: pd.DataFrame,
    genes: Iterable[str],
    prefer: str = "abs",
) -> pd.Series:
    """
    Provide a deterministic tie-break score for candidate genes.

    prefer = "abs"  → mean absolute effect across columns.
    prefer = "up"   → mean positive effect (NaN-safe).
    prefer = "down" → mean negative effect (more negative = larger |score|).

    Returns
    -------
    pd.Series
        Index = genes, values = tie-break scores (higher is better).
    """
    sub = effects.reindex(index=list(genes))
    if prefer == "abs":
        sc = sub.abs().mean(axis=1, skipna=True)
    elif prefer == "up":
        sc = sub.clip(lower=0).mean(axis=1, skipna=True)
    elif prefer == "down":
        sc = (-sub.clip(upper=0)).mean(axis=1, skipna=True)
    else:
        sc = sub.abs().mean(axis=1, skipna=True)
    return sc.fillna(0.0)


def pick_core_ids(
    votes_up: pd.Series,
    votes_dn: pd.Series,
    effects: Optional[pd.DataFrame] = None,
    min_votes: int = config.VOTE_MIN,
    target_up: int = config.CORE_UP_N,
    target_dn: int = config.CORE_DN_N,
) -> Tuple[List[str], List[str], pd.DataFrame]:
    """
    Select consensus core UP/DN genes given vote counts and optional tie-breaks.

    Strategy
    --------
    1) Start with genes meeting the min_votes threshold.
    2) If more than target size → keep highest votes; break ties by mean |effect|.
    3) If fewer than target size → relax threshold stepwise (min_votes-1, -2, ...)
       until reaching the target or exhausting candidates.
    4) If still short, fill by descending vote, then tie-break score.

    Parameters
    ----------
    votes_up, votes_dn : pd.Series
        Vote counts from vote_counts().
    effects : pd.DataFrame, optional
        Gene-by-context matrix to compute tie-break scores; if None, only votes are used.
    min_votes : int
        Minimum votes to initially qualify.
    target_up, target_dn : int
        Target sizes for the core UP/DN gene sets.

    Returns
    -------
    (core_up, core_dn, summary) : (list[str], list[str], pd.DataFrame)
        core_up, core_dn = selected gene lists.
        summary = DataFrame with columns:
            ['gene','dir','votes','score_tie','selected'] sorted by dir/votes/score_tie.

    Notes
    -----
    - 'score_tie' is mean |effect| (UP/DN-specific preference applied).
    - If 'effects' is None, tie-break score is zero (stable order by votes only).
    """
    def _select_side(votes: pd.Series, target: int, prefer: str) -> Tuple[List[str], pd.DataFrame]:
        votes = votes.sort_values(ascending=False)
        if effects is not None and len(votes) > 0:
            tie = _tie_break_scores(effects, votes.index, prefer=prefer)
        else:
            tie = pd.Series(0.0, index=votes.index)

        # Phase A: start at min_votes and relax if needed
        thr = int(min_votes)
        cand = votes[votes >= thr]
        while cand.size < target and thr > 0:
            thr -= 1
            cand = votes[votes >= thr]

        # Phase B: if too many, cut by votes then tie score
        if cand.size > target:
            tmp = pd.DataFrame({"votes": cand, "score_tie": tie.reindex(cand.index).fillna(0.0)})
            tmp = tmp.sort_values(["votes", "score_tie"], ascending=[False, False]).head(target)
            selected = tmp.index.tolist()
        else:
            selected = cand.index.tolist()

        # Phase C: if still short, fill from remaining by votes then tie
        if len(selected) < target:
            remain = votes.drop(index=selected, errors="ignore")
            if not remain.empty:
                tmp = pd.DataFrame({"votes": remain, "score_tie": tie.reindex(remain.index).fillna(0.0)})
                need = target - len(selected)
                extra = tmp.sort_values(["votes", "score_tie"], ascending=[False, False]).head(need).index.tolist()
                selected += extra

        tmp_all = pd.DataFrame({"votes": votes, "score_tie": tie.reindex(votes.index).fillna(0.0)})
        tmp_all["selected"] = tmp_all.index.isin(selected)
        return selected, tmp_all

    up_sel, up_table = _select_side(votes_up, target_up, prefer="up")
    dn_sel, dn_table = _select_side(votes_dn, target_dn, prefer="down")

    up_table = up_table.assign(gene=up_table.index, dir="UP").reset_index(drop=True)
    dn_table = dn_table.assign(gene=dn_table.index, dir="DOWN").reset_index(drop=True)
    summary = (
        pd.concat([up_table, dn_table], ignore_index=True)
        .loc[:, ["gene", "dir", "votes", "score_tie", "selected"]]
        .sort_values(["dir", "selected", "votes", "score_tie"], ascending=[True, False, False, False])
        .reset_index(drop=True)
    )

    return up_sel, dn_sel, summary


def build_consensus_core(
    effects: pd.DataFrame,
    top_n: int = config.N_TOP,
    min_votes: int = config.VOTE_MIN,
    target_up: int = config.CORE_UP_N,
    target_dn: int = config.CORE_DN_N,
    min_non_na: int = 10,
) -> Dict[str, object]:
    """
    Full pipeline: extremes → votes → core sets.

    Parameters
    ----------
    effects : pd.DataFrame
        Gene-by-context matrix with signed effects.
    top_n : int
        Per-column window for UP/DOWN extremes (vote inputs).
    min_votes : int
        Minimum vote threshold for initial qualification.
    target_up, target_dn : int
        Target sizes for the core gene sets.
    min_non_na : int
        Minimum non-NaN values per column to include it in extremes.

    Returns
    -------
    dict
        {
          "core_up": list[str],
          "core_dn": list[str],
          "votes_up": pd.Series,
          "votes_dn": pd.Series,
          "extremes_by_col": dict,
          "summary": pd.DataFrame
        }
    """
    extremes = top_bottom_by_column(effects, top_n=top_n, min_non_na=min_non_na)
    vup, vdn = vote_counts(extremes)
    core_up, core_dn, summary = pick_core_ids(
        vup, vdn, effects=effects, min_votes=min_votes, target_up=target_up, target_dn=target_dn
    )
    return {
        "core_up": core_up,
        "core_dn": core_dn,
        "votes_up": vup,
        "votes_dn": vdn,
        "extremes_by_col": extremes,
        "summary": summary,
    }


# ---------------------------------------------------------------------
# 4) Core score computation
# ---------------------------------------------------------------------
def core_score_from_vector(
    vector: pd.Series | Dict[str, float],
    core_up: Iterable[str],
    core_dn: Iterable[str],
    center: bool = True,
) -> float:
    """
    Compute core score for a single signature/effect vector.

    core_score = mean(z(core_UP)) - mean(z(core_DN))
    where z = (x - mean(x_all)) / std(x_all), if center=True; otherwise raw means.

    Parameters
    ----------
    vector : pd.Series or dict
        Gene-indexed values (z-scores, LFC, etc.). Index should match gene IDs/symbols.
    core_up, core_dn : Iterable[str]
        Core gene sets.
    center : bool
        If True, z-center the vector using mean/std over its non-NaN values.

    Returns
    -------
    float
        Core score. Returns np.nan if not enough genes overlap.

    Notes
    -----
    - Overlap can be partial; genes not present are ignored.
    - If either overlap for UP or DN is empty, returns np.nan.
    """
    s = pd.Series(vector, dtype=float)
    s = s.replace([np.inf, -np.inf], np.nan).dropna()

    if center:
        mu, sd = float(s.mean()), float(s.std(ddof=0))
        if sd == 0 or np.isnan(sd):
            z = s - mu
        else:
            z = (s - mu) / sd
    else:
        z = s

    up_vals = z.reindex(list(core_up)).dropna()
    dn_vals = z.reindex(list(core_dn)).dropna()
    if up_vals.empty or dn_vals.empty:
        return float("nan")
    return float(up_vals.mean() - dn_vals.mean())


def core_score_for_matrix(
    effects: pd.DataFrame,
    core_up: Iterable[str],
    core_dn: Iterable[str],
    center: bool = True,
) -> pd.Series:
    """
    Apply core_score_from_vector() to all columns of a gene-by-context matrix.

    Parameters
    ----------
    effects : pd.DataFrame
        Gene-by-context matrix.
    core_up, core_dn : Iterable[str]
        Core gene sets.
    center : bool
        Whether to z-center each column prior to averaging.

    Returns
    -------
    pd.Series
        Index = columns of `effects`, values = core scores.
    """
    out = {}
    for col in effects.columns:
        out[col] = core_score_from_vector(effects[col], core_up, core_dn, center=center)
    return pd.Series(out, dtype=float)
