# src/vitd_utils/dose.py

"""
dose.py

Utility functions to analyze dose–response patterns in transcriptomic data.
This module provides helpers for:
- Splitting conditions into low/high dose groups.
- Testing monotonic trends across doses.
- Estimating dose–response slopes.

Author: Paula Irazoqui
Project: Vitamin D Transcriptomic Profiling (LINCS L1000)
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------
# Dose binning
# ---------------------------------------------------------
def binarize_dose(dose_values, threshold=None):
    """
    Convert continuous doses into 'low' vs 'high' categories.

    Parameters
    ----------
    dose_values : array-like
        Numeric dose values (µM or nM, depending on metadata).
    threshold : float, optional
        Threshold for splitting low vs high dose.
        If None, uses the median of the values.

    Returns
    -------
    pd.Series
        Binary categories: "low" or "high".
    """
    if threshold is None:
        threshold = np.median(dose_values)

    return pd.Series(
        ["low" if d <= threshold else "high" for d in dose_values],
        index=np.arange(len(dose_values))
    )


# ---------------------------------------------------------
# Dose–response monotonicity
# ---------------------------------------------------------
def dose_monotonicity(doses, responses):
    """
    Test monotonic relationship between dose and response using Spearman correlation.

    Parameters
    ----------
    doses : array-like
        Numeric dose values.
    responses : array-like
        Transcriptomic response metric (e.g., core_score).

    Returns
    -------
    dict
        {
            "rho": Spearman correlation coefficient,
            "pvalue": two-sided p-value
        }
    """
    rho, pval = spearmanr(doses, responses)
    return {"rho": rho, "pvalue": pval}


# ---------------------------------------------------------
# Dose–response slope estimation
# ---------------------------------------------------------
def dose_response_slope(doses, responses):
    """
    Estimate slope of dose–response using log10(dose) as predictor.

    Parameters
    ----------
    doses : array-like
        Numeric dose values.
    responses : array-like
        Transcriptomic response metric.

    Returns
    -------
    dict
        {
            "slope": regression coefficient for log10(dose),
            "intercept": model intercept,
            "r2": coefficient of determination
        }
    """
    X = np.log10(np.array(doses)).reshape(-1, 1)
    y = np.array(responses)

    model = LinearRegression()
    model.fit(X, y)

    return {
        "slope": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "r2": float(model.score(X, y))
    }


# ---------------------------------------------------------
# OLS with robust (HC3) standard errors
# ---------------------------------------------------------
import statsmodels.api as sm

def ols_hc3(doses, responses):
    """
    Fit OLS regression with log10(dose) as predictor and HC3 robust errors.

    Parameters
    ----------
    doses : array-like
        Numeric dose values.
    responses : array-like
        Transcriptomic response metric.

    Returns
    -------
    results : statsmodels.regression.linear_model.RegressionResultsWrapper
        Fitted OLS model with HC3 robust standard errors.
    """
    X = sm.add_constant(np.log10(np.array(doses)))
    y = np.array(responses)

    model = sm.OLS(y, X).fit(cov_type="HC3")
    return model


# ---------------------------------------------------------
# Helpers for forest plot
# ---------------------------------------------------------
def summarize_forest(models, labels):
    """
    Summarize coefficients and 95% CI for forest plots.

    Parameters
    ----------
    models : list
        List of fitted OLS models (from ols_hc3).
    labels : list
        Labels corresponding to each model (e.g., cell line names).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: label, coef, ci_low, ci_high, pvalue.
    """
    rows = []
    for model, label in zip(models, labels):
        coef = model.params[1]       # slope
        se = model.bse[1]            # robust SE
        ci_low = coef - 1.96 * se
        ci_high = coef + 1.96 * se
        pval = model.pvalues[1]

        rows.append({
            "label": label,
            "coef": coef,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "pvalue": pval
        })

    return pd.DataFrame(rows)
