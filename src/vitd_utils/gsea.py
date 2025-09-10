# src/vitd_utils/gsea.py
"""
GSEA / enrichment utilities for the Vitamin D transcriptomic profiling project.

This module provides:
- Building of preranked tables from gene-wise scores.
- Loading of MSigDB/Reactome GMT libraries.
- A fast GSEA-like fallback (weight-permutation) enrichment.
- A resumable runner that executes permutations in chunks with checkpoints.
- A compact dot-plot visualization for top pathways.

Design goals
------------
- Pure-Python implementation (no hard dependency on external GSEA packages).
- Reasonable defaults taken from vitd_utils.config but overridable by args.
- Resumability for long runs (e.g., 400–1000 permutations).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from textwrap import fill
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns

from .idsymbols import map_symbols_or_ids
from . import config


__all__ = [
    "make_preranked",
    "make_enrichr_lists",
    "load_gmt",
    "prepare_gene_sets",
    "preranked_enrich_fallback_fast",
    "run_enrichment_axis_resumable",
    "dotplot_top",
]


# ---------------------------------------------------------------------
# Preranked builders
# ---------------------------------------------------------------------
def make_preranked(series: pd.Series, sym_map: pd.Series) -> pd.DataFrame:
    """
    Build a two-column DataFrame ('gene','score') for GSEA Preranked.

    Parameters
    ----------
    series : pd.Series
        Index = gene_id (any dtype), values = numeric scores (float-like).
    sym_map : pd.Series
        Mapping gene_id(str) -> gene_symbol (may contain NaN). Use build_symbol_map().

    Returns
    -------
    pd.DataFrame
        Columns: 'gene' (symbols with fallback to id), 'score' (float).
        - Deduplicated at the symbol level keeping the row with largest |score|.
        - Sorted by 'score' descending.
    """
    s = pd.to_numeric(series, errors="coerce")
    s.index = s.index.astype(str)

    symbols = pd.Series(map_symbols_or_ids(s.index, sym_map), index=s.index, dtype=object)
    df = pd.DataFrame({"gene": symbols.values, "score": s.values}, index=s.index)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["score"])

    # order by |score| desc; keep the entry with largest |score| per gene symbol
    order = df["score"].abs().sort_values(ascending=False).index
    df = df.loc[order].drop_duplicates(subset="gene", keep="first")
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def make_enrichr_lists(preranked_df: pd.DataFrame, top_n: int = 200) -> Dict[str, List[str]]:
    """
    Build simple Enrichr-like gene lists from a preranked table.

    Parameters
    ----------
    preranked_df : pd.DataFrame
        Output of make_preranked() with 'gene','score' columns.
    top_n : int, default 200
        Number of genes to take from each extreme.

    Returns
    -------
    dict
        {"UP": [...top_n genes...], "DOWN": [...top_n genes... (reversed tail)]}
    """
    up = preranked_df["gene"].head(top_n).tolist()
    down = preranked_df["gene"].tail(top_n).tolist()[::-1]
    return {"UP": up, "DOWN": down}


# ---------------------------------------------------------------------
# GMT loading / preparation
# ---------------------------------------------------------------------
def load_gmt(path: str | Path) -> Dict[str, set]:
    """
    Load a GMT file into a dict: term -> set(members).

    Parameters
    ----------
    path : str | Path
        Path to a GMT file (tab-delimited; name, url, members...).

    Returns
    -------
    dict
        Mapping from pathway name to a set of gene symbols.
    """
    gs: Dict[str, set] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                gs[parts[0]] = set(g for g in parts[2:] if g)
    return gs


def prepare_gene_sets(lib_entry: str | Mapping[str, Iterable[str]] | None) -> Optional[Dict[str, set]]:
    """
    Normalize a library input into {term: set([...])}.

    Parameters
    ----------
    lib_entry : str | Mapping | None
        - If str: treated as GMT path and loaded.
        - If Mapping: assumed to be {term: iterable_of_genes}.
        - If None: returns None.

    Returns
    -------
    dict | None
        A dictionary of gene sets or None if unavailable.
    """
    if lib_entry is None:
        return None
    if isinstance(lib_entry, (str, Path)):
        p = Path(lib_entry)
        if not p.exists():
            return None
        return load_gmt(p)
    if isinstance(lib_entry, Mapping):
        return {k: (set(v) if not isinstance(v, set) else v) for k, v in lib_entry.items()}
    return None


# ---------------------------------------------------------------------
# Fast GSEA-like fallback (permute weights; reuse hit/miss structures)
# ---------------------------------------------------------------------
def _running_sum_es(weights: np.ndarray, hit: np.ndarray, inc_miss: np.ndarray) -> Tuple[float, int]:
    """
    Compute running-sum enrichment score for a given weight vector and hit/miss.

    Parameters
    ----------
    weights : np.ndarray
        Normalized weights along the ranked gene list (sum=1). Shape (N,)
    hit : np.ndarray[bool]
        Boolean vector marking hits (True for genes in the set). Shape (N,)
    inc_miss : np.ndarray
        Precomputed increment for misses (constant per term). Shape (N,)

    Returns
    -------
    (es, argmax_index)
        ES = max running-sum value, argmax index for the leading-edge fraction calc.
    """
    Nh = int(hit.sum())
    if Nh == 0 or Nh == len(hit):
        return 0.0, 0
    w_hit_sum = weights[hit].sum()
    if w_hit_sum <= 0:
        inc_hit = np.zeros_like(weights); inc_hit[hit] = 1.0 / Nh
    else:
        inc_hit = np.zeros_like(weights); inc_hit[hit] = weights[hit] / w_hit_sum
    rs = np.cumsum(inc_hit - inc_miss)
    j = int(rs.argmax())
    return float(rs[j]), j


def preranked_enrich_fallback_fast(
    preranked_df: pd.DataFrame,
    gene_sets: Mapping[str, Iterable[str]],
    perm_n: int = 200,
    random_state: int = 0,
    min_size: int = 15,
    max_size: int = 500,
) -> pd.DataFrame:
    """
    Fast GSEA-like fallback:
      - Sort once (descending score).
      - Build hit masks and miss increments once per term.
      - Permute only the weights (abs(scores)) across permutations.

    Parameters
    ----------
    preranked_df : pd.DataFrame
        Output of make_preranked().
    gene_sets : Mapping[str, Iterable[str]]
        Dictionary {term: iterable_of_genes}.
    perm_n : int, default 200
        Number of permutations for null distribution.
    random_state : int, default 0
        RNG seed.
    min_size, max_size : int, default 15, 500
        Filter gene sets outside this size range (speed/stability).

    Returns
    -------
    pd.DataFrame
        Columns: term, ES, pval, fdr_bh, set_size, leading_edge_frac
    """
    genes = preranked_df["gene"].astype(str).values
    scores = pd.to_numeric(preranked_df["score"], errors="coerce").fillna(0).values
    order = np.argsort(scores)[::-1]
    genes = genes[order]
    weights = np.abs(scores[order]).astype(float)
    total_w = weights.sum()
    weights = (weights / total_w) if total_w > 0 else np.ones_like(weights) / len(weights)

    idx_map = {g: i for i, g in enumerate(genes)}
    N = len(genes)
    rng = np.random.RandomState(random_state)

    rows = []
    for term, members in gene_sets.items():
        # Map members to ranked positions
        idx = np.fromiter((idx_map.get(g, -1) for g in members), dtype=int)
        idx = idx[idx >= 0]
        Nh = int(idx.size)
        if Nh < min_size or Nh > max_size:
            continue

        hit = np.zeros(N, dtype=bool); hit[idx] = True
        miss = ~hit; miss_count = int(miss.sum())
        if miss_count == 0:
            continue
        inc_miss = miss.astype(float) / float(miss_count)

        # Observed ES
        es_obs, le_idx = _running_sum_es(weights, hit, inc_miss)
        le_frac = float(hit[: le_idx + 1].sum() / max(1, Nh))

        # Null ES via weight permutations
        more = 0
        for _ in range(perm_n):
            w = weights.copy()
            rng.shuffle(w)
            es_null, _ = _running_sum_es(w, hit, inc_miss)
            if abs(es_null) >= abs(es_obs):
                more += 1
        pval = (more + 1) / (perm_n + 1)

        rows.append(
            {"term": term, "ES": float(es_obs), "pval": float(pval),
             "set_size": Nh, "leading_edge_frac": le_frac}
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        out["fdr_bh"] = multipletests(out["pval"].values, method="fdr_bh")[1]
        out = out.sort_values(["fdr_bh", "ES"], ascending=[True, False]).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------
# Resumable runner (axis → library → group), with checkpoints
# ---------------------------------------------------------------------
def _rank_checksum(preranked_df: pd.DataFrame, k: int = 500) -> str:
    """
    Hash top-k (gene, score) pairs to detect ranking changes across sessions.
    """
    top = preranked_df[["gene", "score"]].head(k).astype(str).values.ravel().tolist()
    blob = "|".join(top).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()


def _checkpoint_paths(axis: str, lib_name: str, group: str | int) -> Tuple[Path, Path]:
    stem = f"{axis}_{lib_name}_{str(group)}".replace(" ", "_")
    outdir = (config.RESULTS_DIR / "enrichment")
    outdir.mkdir(parents=True, exist_ok=True)
    return (outdir / f"{stem}.checkpoint.json", outdir / f"{stem}.preview.csv")


def _compute_structs_for_terms(
    preranked_df: pd.DataFrame,
    gene_sets: Mapping[str, Iterable[str]],
    min_size: int,
    max_size: int,
) -> dict:
    """
    Precompute structures reused across permutations: hit masks, miss increments,
    and observed ES for each term.
    """
    genes = preranked_df["gene"].astype(str).values
    scores = pd.to_numeric(preranked_df["score"], errors="coerce").fillna(0).values
    order = np.argsort(scores)[::-1]
    genes = genes[order]
    weights = np.abs(scores[order]).astype(float)
    tot = weights.sum()
    weights = (weights / tot) if tot > 0 else np.ones_like(weights) / len(weights)

    idx_map = {g: i for i, g in enumerate(genes)}
    N = len(genes)

    terms, hit_masks, inc_miss_list, base = [], [], [], []
    for term, members in gene_sets.items():
        idx = np.fromiter((idx_map.get(g, -1) for g in members), dtype=int)
        idx = idx[idx >= 0]
        Nh = int(idx.size)
        if Nh < min_size or Nh > max_size:
            continue
        hit = np.zeros(N, dtype=bool); hit[idx] = True
        miss = ~hit; miss_count = int(miss.sum())
        if miss_count == 0:
            continue
        inc_miss = miss.astype(float) / float(miss_count)
        # observed ES
        es_obs, le_idx = _running_sum_es(weights, hit, inc_miss)
        le_frac = float(hit[: le_idx + 1].sum() / max(1, Nh))

        terms.append(term)
        hit_masks.append(hit)
        inc_miss_list.append(inc_miss)
        base.append({"term": term, "ES": float(es_obs), "set_size": Nh, "leading_edge_frac": le_frac})

    return {
        "genes": genes,
        "weights": weights,
        "terms": terms,
        "hit_masks": hit_masks,
        "inc_miss": inc_miss_list,
        "base": base,
    }


def _resume_or_init_state(axis, lib_name, group, preranked_df, base_rows):
    ckp_path, csv_path = _checkpoint_paths(axis, lib_name, group)
    checksum = _rank_checksum(preranked_df)
    if ckp_path.exists():
        with open(ckp_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("checksum") == checksum:
            return state, ckp_path, csv_path, checksum
        print(f"[resume] Ranking changed for {axis}/{lib_name}/{group} — restarting.")
    # initialize
    state = {
        "checksum": checksum,
        "perm_done": 0,
        "terms": {
            r["term"]: {
                "more_extreme": 0,
                "ES": r["ES"],
                "set_size": r["set_size"],
                "leading_edge_frac": r["leading_edge_frac"],
            }
            for r in base_rows
        },
    }
    return state, ckp_path, csv_path, checksum


def _write_preview_csv(state: dict, csv_path: Path) -> None:
    rows = []
    perm_done = max(1, int(state["perm_done"]))
    for term, rec in state["terms"].items():
        pval = (rec["more_extreme"] + 1) / (perm_done + 1)
        rows.append(
            {
                "term": term,
                "ES": rec["ES"],
                "pval": pval,
                "set_size": rec["set_size"],
                "leading_edge_frac": rec["leading_edge_frac"],
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        df["fdr_bh"] = multipletests(df["pval"].values, method="fdr_bh")[1]
        df = df.sort_values(["fdr_bh", "ES"], ascending=[True, False])
    df.to_csv(csv_path, index=False)


def _run_group_chunked(
    axis: str,
    lib_name: str,
    group: str | int,
    preranked_df: pd.DataFrame,
    gene_sets: Mapping[str, Iterable[str]],
    target_perms: int,
    chunk_perms: int,
    random_state: int,
    min_size: int,
    max_size: int,
) -> Optional[pd.DataFrame]:
    """
    Execute/resume permutations in chunks for one (axis, library, group).
    Updates checkpoint JSON + preview CSV on every chunk.
    """
    structs = _compute_structs_for_terms(preranked_df, gene_sets, min_size, max_size)
    if not structs["terms"]:
        print(f"[{lib_name}] {axis}={group}: no terms after size filter; skip.")
        return None

    state, ckp_path, csv_path, checksum = _resume_or_init_state(axis, lib_name, group, preranked_df, structs["base"])

    # Map 'term' to index for quick access
    term_idx = {t: i for i, t in enumerate(structs["terms"])}
    rng = np.random.RandomState(random_state)
    weights = structs["weights"]
    hit_masks = structs["hit_masks"]
    inc_miss_list = structs["inc_miss"]

    while state["perm_done"] < target_perms:
        to_run = min(chunk_perms, target_perms - state["perm_done"])
        g0 = time.time()
        for _ in range(to_run):
            w = weights.copy()
            rng.shuffle(w)
            for t, i in term_idx.items():
                hit = hit_masks[i]
                inc_miss = inc_miss_list[i]
                Nh = int(state["terms"][t]["set_size"])
                w_hit_sum = w[hit].sum()
                if w_hit_sum <= 0:
                    inc_hit = np.zeros_like(w); inc_hit[hit] = 1.0 / Nh
                else:
                    inc_hit = np.zeros_like(w); inc_hit[hit] = w[hit] / w_hit_sum
                rs_perm = np.cumsum(inc_hit - inc_miss)
                if np.max(np.abs(rs_perm)) >= abs(state["terms"][t]["ES"]):
                    state["terms"][t]["more_extreme"] += 1

        state["perm_done"] += to_run
        with open(ckp_path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        _write_preview_csv(state, csv_path)
        print(f"[{lib_name}] {axis}={group} | +{to_run} perms in {time.time()-g0:.1f}s "
              f"(done {state['perm_done']}/{target_perms})")

    # Build final DataFrame
    perm_done = max(1, int(state["perm_done"]))
    rows = []
    for term, rec in state["terms"].items():
        pval = (rec["more_extreme"] + 1) / (perm_done + 1)
        rows.append(
            {
                "term": term,
                "ES": rec["ES"],
                "pval": pval,
                "set_size": rec["set_size"],
                "leading_edge_frac": rec["leading_edge_frac"],
                "group": str(group),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        df["fdr_bh"] = multipletests(df["pval"].values, method="fdr_bh")[1]
        df = df.sort_values(["fdr_bh", "ES"], ascending=[True, False]).reset_index(drop=True)
    print(f"✔ [{lib_name}] {axis}={group} finished; perms={state['perm_done']}")
    return df


def run_enrichment_axis_resumable(
    axis: str = "cell",
    libraries: Optional[Mapping[str, str | Mapping[str, Iterable[str]]]] = None,
    target_perms: int = config.PERM_N,
    chunk_perms: int = config.CHUNK_PERMS,
    min_size: int = 15,
    max_size: int = 500,
    random_state: int = config.RANDOM_STATE,
) -> Dict[str, Dict[str, Optional[pd.DataFrame]]]:
    """
    Orchestrate enrichment per axis ("cell" or "analog"), per library, per group.
    Uses resumable checkpoints per (axis, library, group).

    Returns
    -------
    dict
        {library_name: {group: DataFrame or None}}
    """
    assert axis in ("cell", "analog")
    libraries = dict(libraries or {})
    preranked_dict = globals().get(
        "gsea_preranked_by_cell" if axis == "cell" else "gsea_preranked_by_analog", {}
    )
    results: Dict[str, Dict[str, Optional[pd.DataFrame]]] = {}

    for lib_name, lib_entry in libraries.items():
        gene_sets = prepare_gene_sets(lib_entry)
        if not gene_sets:
            print(f"[warn] Library '{lib_name}' not found/empty — skipping.")
            results[lib_name] = {}
            continue

        lib_out: Dict[str, Optional[pd.DataFrame]] = {}
        for group, rnk in preranked_dict.items():
            if rnk is None or rnk.empty:
                continue
            df = _run_group_chunked(
                axis, lib_name, group, rnk, gene_sets,
                target_perms, chunk_perms, random_state, min_size, max_size
            )
            lib_out[group] = df
        results[lib_name] = lib_out

    return results


# ---------------------------------------------------------------------
# Visualization (improved)
# ---------------------------------------------------------------------

def dotplot_top(
    enr_results: Mapping[str, Optional[pd.DataFrame]],
    lib_name: str,
    axis: str = "cell",
    top_n: int = config.ENR_TOP_PATHWAYS,
    fdr_cutoff: float = 0.05,
    groups: Optional[List[str]] = None,      # e.g. ["A549","HA1E","MCF7","PC3","U2OS"]
    wrap_width: int = 28,
    vmax_cap: float = 2.5,
    fig_width: float = 14.0,                  # wider canvas, fixed height scaling
    left_margin: float = 0.30,               # reserved for long labels (0–1)
    bottom_pad: float = 0.26,                # room for both legends at bottom
    point_sizes: tuple = (26, 140),          # (min,max) marker sizes
) -> None:
    """
    Create a publication-optimized dot plot summarizing enrichment results.

    Parameters
    ----------
    enr_results : Mapping[str, Optional[pd.DataFrame]]
        Dictionary {group: enrichment_results}, where each DataFrame must contain:
        - 'term' (str): pathway name
        - 'ES' (float): enrichment score
        - 'fdr_bh' (float): adjusted p-value (FDR)
        - 'set_size' (int): gene set size
    lib_name : str
        Name of the gene set library (for plot titles/labels).
    axis : {"cell", "analog"}, default "cell"
        Axis of grouping (cell lines vs analogs).
    top_n : int, default config.ENR_TOP_PATHWAYS
        Number of top pathways to keep (after FDR filtering).
    fdr_cutoff : float, default 0.05
        Only pathways with FDR < cutoff are considered before ranking.
    groups : list of str, optional
        Fixed x-axis categories (all shown even if missing results).
    wrap_width : int, default 28
        Maximum characters per line for wrapped pathway labels.
    vmax_cap : float, default 2.5
        Upper cap for -log10(FDR) color scale.
    fig_width : float, default 14.0
        Base figure width (scales with number of groups).
    left_margin : float, default 0.30
        Space reserved for long y-axis labels (fraction of figure width).
    bottom_pad : float, default 0.26
        Extra padding at bottom for legends (size + colorbar).
    point_sizes : tuple(int, int), default (26, 140)
        Min and max marker sizes used for scaling by set size.

    Returns
    -------
    None
        Displays the plot (and saves a PNG if config.SAVE_FIGS is True).

    Notes
    -----
    - Color encodes significance (−log10 FDR), capped by `vmax_cap`.
    - Point size encodes gene set size.
    - Terms are ranked by median significance across groups.
    - Legends: set size (left bottom) and horizontal colorbar (right bottom).
    """
    # ------------- collect rows per group (filter by FDR, then take top_n) -------------
    coll = []
    for g, df in enr_results.items():
        if df is None or df.empty:
            continue
        tmp = df.copy()
        if fdr_cutoff is not None:
            tmp = tmp.loc[tmp["fdr_bh"] < fdr_cutoff]
        if tmp.empty:
            continue
        tmp["neglogFDR"] = -np.log10(tmp["fdr_bh"].replace(0, 1e-300))
        tmp = tmp.sort_values(["fdr_bh", "ES"], ascending=[True, False]).head(top_n)
        tmp["group"] = str(g)
        coll.append(tmp[["term", "group", "neglogFDR", "set_size"]])

    if not coll:
        print(f"[info] No results to plot for {lib_name}.")
        return

    M = pd.concat(coll, ignore_index=True)

    # Keep top_n *unique* terms overall by median signal
    keep_terms = (
        M.groupby("term")["neglogFDR"].median().sort_values(ascending=False).head(top_n).index
    )
    M = M[M["term"].isin(keep_terms)].copy()

    # Desired x-axis groups (ensure all five are shown)
    group_order = sorted(M["group"].unique()) if groups is None else list(groups)

    # Wrap long pathway labels for readability
    def _pretty(t: str) -> str:
        return fill(str(t).replace("_", " "), width=wrap_width)
    M["term_plot"] = M["term"].map(_pretty)

    # Order y by median strength
    term_order = (
        M.groupby("term_plot")["neglogFDR"].median().sort_values(ascending=True).index.tolist()
    )

    # Enforce categorical ordering
    M["group"] = pd.Categorical(M["group"], categories=group_order, ordered=True)
    M["term_plot"] = pd.Categorical(M["term_plot"], categories=term_order, ordered=True)

    # --- Full grid + dummy layer: make all group ticks exist even with no points ---
    grid = pd.MultiIndex.from_product([term_order, group_order],
                                      names=["term_plot", "group"]).to_frame(index=False)
    merged = grid.merge(M, on=["term_plot", "group"], how="left")
    missing_mask = merged["neglogFDR"].isna()

    # Color scale
    vmin = 0.0
    vmax = min(max(M["neglogFDR"].max(), vmin + 0.1), vmax_cap)

    # ----------------------- figure layout (wider, same height logic) -------------------
    fig_h = max(5.0, 0.55 * len(term_order))
    fig_w = max(fig_width, 1.1 * len(group_order))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # 1) Invisible dummy points to register categories
    if missing_mask.any():
        dummy = merged.loc[missing_mask, ["group", "term_plot"]].copy()
        dummy["neglogFDR"] = vmin
        dummy["set_size"] = 1
        sns.scatterplot(
            data=dummy,
            x="group", y="term_plot",
            hue="neglogFDR", palette="viridis", hue_norm=(vmin, vmax),
            size="set_size", sizes=point_sizes,
            linewidth=0, edgecolor=None, legend=False, ax=ax, alpha=0.0
        )

    # 2) Real points
    sns.scatterplot(
        data=M,
        x="group", y="term_plot",
        hue="neglogFDR", palette="viridis", hue_norm=(vmin, vmax),
        size="set_size", sizes=point_sizes,
        linewidth=0.3, edgecolor="black",
        legend=False, ax=ax, alpha=1.0
    )

    # Axis labels/title
    ax.set_xlabel("Group (cell line)" if axis == "cell" else "Group (analog)")
    ax.set_ylabel(f"Top pathways ({lib_name})")
    ax.set_title(f"Enrichment summary — {lib_name} by {axis}")

    # --- Force x ticks for ALL groups (even if some had no points) ---
    ax.set_xticks(range(len(group_order)))
    ax.set_xticklabels(group_order, rotation=45, ha="right")

    # ------------------------ legends at the bottom, side by side -----------------------
    # Reserve space (left for labels, bottom for both legends, right small margin)
    plt.subplots_adjust(left=left_margin, right=0.86, bottom=bottom_pad)

    # (a) Size legend (left bottom)
    from matplotlib.lines import Line2D
    sz = M["set_size"].to_numpy()
    pos = sz[sz > 0]
    if pos.size > 0:
        ticks = sorted(set([int(np.nanmin(pos)), int(np.nanmax(pos))]))
    else:
        ticks = [1]
    handles = [
        Line2D([0], [0], marker='o', linestyle='',
               markersize=np.interp(v, [max(1, sz.min()), max(1, sz.max())], [6, 18]),
               color='grey', alpha=0.75, label=str(v))
        for v in ticks
    ]
    ax.legend(handles=handles, title="set_size",
              loc="upper left", bbox_to_anchor=(0.02, -0.2),
              frameon=False, ncol=len(handles))

    # (b) Horizontal colorbar (right bottom)
    cbar_ax = fig.add_axes([0.42, 0.06, 0.44, 0.028])  # [left, bottom, width, height]
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm); sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    cbar.set_label("-log10(FDR)")

    # Save if requested
    if getattr(config, "SAVE_FIGS", False):
        out = config.FIG_DIR / f"dotplot_{axis}_{lib_name}.png"
        fig.savefig(out, dpi=400, bbox_inches="tight")
        print(f"[saved] {out}")

    plt.show()
