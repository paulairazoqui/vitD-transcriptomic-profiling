# src/vitd_utils/plotting.py
"""
Plotting helpers for the Vitamin D transcriptomic profiling project.

This module provides:
- savefig: centralized figure saving respecting config.SAVE_FIGS and FIG_DIR.
- forest_from_models: forest plot of slopes with HC3 CI (uses dose.summarize_forest).
- forest_from_summary: forest plot from a precomputed summary DataFrame.
- box_strip: combined boxplot + stripplot with optional group sizes and p-values.

Design goals
------------
- Minimal, publication-ready defaults.
- No hardcoded paths; uses vitd_utils.config.
- Functions return the matplotlib Axes for further tweaking in notebooks.

Author: Paula Irazoqui
Project: Vitamin D Transcriptomic Profiling (LINCS L1000)
"""

from __future__ import annotations
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from . import config

__all__ = [
    "savefig",
    "forest_from_models",
    "forest_from_summary",
    "box_strip",
]


# ---------------------------------------------------------------------
# General save helper
# ---------------------------------------------------------------------
def savefig(fig: Optional[plt.Figure] = None, filename: str = "figure.png", dpi: int = 400) -> None:
    """
    Save current or provided figure into config.FIG_DIR if config.SAVE_FIGS=True.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or None
        Figure to save. If None, uses plt.gcf().
    filename : str
        Output filename (no directories).
    dpi : int
        Resolution for raster formats.
    """
    if not getattr(config, "SAVE_FIGS", False):
        return
    fig = fig or plt.gcf()
    out = config.FIG_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    print(f"[saved] {out}")


# ---------------------------------------------------------------------
# Forest plots
# ---------------------------------------------------------------------
def forest_from_summary(
    df: pd.DataFrame,
    x: str = "coef",
    y: str = "label",
    ci_low: str = "ci_low",
    ci_high: str = "ci_high",
    p_col: str = "pvalue",
    title: Optional[str] = None,
    sort: str = "coef",  # "coef" | "abs" | "none"
    zero_line: bool = True,
    figsize: Optional[tuple] = None,
    point_size: int = 50,
) -> plt.Axes:
    """
    Forest plot from a summary table (e.g., output of dose.summarize_forest).

    Expected columns: [label, coef, ci_low, ci_high, pvalue].

    Parameters
    ----------
    df : pd.DataFrame
        Summary of effects and CIs.
    sort : str
        Sort order: "coef" (ascending), "abs" (by |coef| descending), or "none".
    zero_line : bool
        Draw a vertical line at x=0 (no effect).
    """
    work = df[[y, x, ci_low, ci_high, p_col]].dropna().copy()

    if sort == "coef":
        work = work.sort_values(x, ascending=True)
    elif sort == "abs":
        work = work.reindex(work[x].abs().sort_values(ascending=False).index)
    # else "none": keep incoming order

    work[y] = work[y].astype(str)
    ylabels = work[y].tolist()

    if figsize is None:
        figsize = (max(6, 0.45 * len(ylabels) + 4), max(4.5, 0.35 * len(ylabels) + 1))
    fig, ax = plt.subplots(figsize=figsize)

    # Horizontal CI lines
    ax.hlines(y=np.arange(len(work)), xmin=work[ci_low], xmax=work[ci_high], lw=2, alpha=0.9)
    # Points
    ax.scatter(work[x], np.arange(len(work)), s=point_size, zorder=3)

    if zero_line:
        ax.axvline(0, ls="--", lw=1, color="grey", alpha=0.7, zorder=1)

    # Y-axis labels
    ax.set_yticks(np.arange(len(work)))
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Effect size (slope)")
    ax.set_ylabel("")
    if title:
        ax.set_title(title)

    # Optional annotate p-values
    # Keep concise: only show if clearly significant
    for i, (_, row) in enumerate(work.iterrows()):
        try:
            p = float(row[p_col])
        except Exception:
            p = np.nan
        if np.isfinite(p) and p < 0.05:
            ax.text(row[x], i, f"  p={p:.3g}", va="center", fontsize=9)

    plt.tight_layout()
    return ax


def forest_from_models(
    models: Sequence,
    labels: Sequence[str],
    title: Optional[str] = None,
    sort: str = "coef",
    **kwargs,
) -> plt.Axes:
    """
    Forest plot directly from a list of statsmodels OLS (HC3) results.

    Parameters
    ----------
    models : list[RegressionResultsWrapper]
        Output of vitd_utils.dose.ols_hc3(...)
    labels : list[str]
        Labels for each model (e.g., cell line names).
    title : str or None
        Title to set on the plot.
    sort : str
        Passed to forest_from_summary.
    kwargs : dict
        Forwarded to forest_from_summary (e.g., figsize, point_size).
    """
    # Local import to avoid circular deps at module import time
    from .dose import summarize_forest
    df = summarize_forest(models, labels)
    ax = forest_from_summary(df, title=title, sort=sort, **kwargs)
    return ax


# ---------------------------------------------------------------------
# Box + strip helper
# ---------------------------------------------------------------------
def box_strip(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    order: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    show_n: bool = True,
    test: Optional[str] = None,  # "ttest" | "mannwhitney" | None
    alpha: float = 0.05,
    figsize: tuple = (6.5, 4.5),
    jitter: float = 0.25,
    dodge: bool = True,
    box_kwargs: Optional[dict] = None,
    strip_kwargs: Optional[dict] = None,
) -> plt.Axes:
    """
    Combined boxplot + stripplot with optional group sizes and simple p-value.

    Parameters
    ----------
    df : pd.DataFrame
        Long-form dataset.
    x, y : str
        Column names for grouping and value.
    hue : str or None
        Optional second grouping for color dodge.
    order : sequence or None
        Explicit category order for x-axis.
    test : {"ttest","mannwhitney",None}
        If set, performs a simple two-group test using all data in each x-level
        (ignores hue). Prints/annotates p-value when x has exactly 2 levels.
    """
    box_kwargs = dict(color="white", fliersize=0, linewidth=1.2) | (box_kwargs or {})
    strip_kwargs = dict(size=4, alpha=0.75, jitter=jitter, dodge=dodge) | (strip_kwargs or {})

    data = df[[x, y] + ([hue] if hue else [])].dropna()
    if order is None:
        order = list(pd.unique(data[x]))
    fig, ax = plt.subplots(figsize=figsize)

    sns.boxplot(data=data, x=x, y=y, order=order, hue=hue, dodge=dodge, ax=ax, **box_kwargs)
    sns.stripplot(data=data, x=x, y=y, order=order, hue=hue, dodge=dodge, ax=ax, **strip_kwargs)

    # Avoid double legends if both layers used hue
    if hue:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[:len(pd.unique(data[hue]))], labels[:len(pd.unique(data[hue]))], title=hue)
    else:
        ax.legend_.remove() if ax.get_legend() else None

    # Show group sizes (n) above boxes
    if show_n:
        for i, cat in enumerate(order):
            n = data.loc[data[x] == cat, y].notna().sum()
            ymax = data[y].max(skipna=True)
            ax.text(i, ymax, f"n={n}", ha="center", va="bottom", fontsize=9)

    if title:
        ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.tight_layout()

    # Optional simple two-group test across x levels (ignores hue)
    if test is not None:
        cats = list(order)
        if len(cats) == 2:
            a = data.loc[data[x] == cats[0], y].astype(float).dropna().values
            b = data.loc[data[x] == cats[1], y].astype(float).dropna().values
            p = np.nan
            try:
                if test == "ttest":
                    from scipy.stats import ttest_ind
                    stat, p = ttest_ind(a, b, equal_var=False, nan_policy="omit")
                elif test == "mannwhitney":
                    from scipy.stats import mannwhitneyu
                    stat, p = mannwhitneyu(a, b, alternative="two-sided")
            except Exception:
                p = np.nan
            if np.isfinite(p):
                y_max = max(np.nanmax(a) if a.size else 0, np.nanmax(b) if b.size else 0)
                y_min = min(np.nanmin(a) if a.size else 0, np.nanmin(b) if b.size else 0)
                y_bar = y_max + 0.07 * (y_max - y_min if y_max > y_min else 1.0)
                ax.plot([0, 0, 1, 1], [y_bar, y_bar*1.02, y_bar*1.02, y_bar], lw=1.2, c="k")
                sig = "*" if p < alpha else "ns"
                ax.text(0.5, y_bar*1.03, f"p={p:.3g} ({sig})", ha="center", va="bottom", fontsize=9)

    return ax
