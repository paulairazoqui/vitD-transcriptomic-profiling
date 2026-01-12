# Global Machine Learning Baseline

## Overview

This module implements a **global machine learning baseline** for the project.  
Its primary goal is to establish a **reproducible and interpretable reference model** against which more complex or targeted approaches can be evaluated.

Rather than optimizing for maximum predictive performance, this baseline focuses on:
- Stability
- Transparency
- Robustness across conditions
- Clear separation between signal and noise

All subsequent modeling efforts are expected to be compared against the results obtained here.

---

## Objectives

The specific objectives of this baseline are:

1. To quantify how much predictive signal is present at a **global level**, without conditioning on specific subgroups.
2. To evaluate whether linear or weakly regularized relationships are sufficient to explain the target variable.
3. To provide an interpretable model that allows inspection of feature contributions.
4. To define a lower-bound performance benchmark for future models.

---

## Data Preparation and Scope

This baseline operates on the **fully aggregated dataset**, using all available samples after standard preprocessing steps defined upstream in the pipeline.

Key characteristics of this approach:
- No stratification by subgroup, condition, or experimental batch.
- No feature engineering beyond standardized transformations.
- No domain-specific filtering or manual feature selection.

This design choice is intentional and ensures that the model reflects **global structure only**.

---

## Feature Scaling

All features are standardized prior to modeling.

Rationale:
- Ensures comparability across features with different scales.
- Required for regularized linear models.
- Prevents dominance of high-variance features.

Standardization is applied **after train–test splitting** to avoid data leakage.

---

## Model Selection

### Baseline Model: Elastic Net Regression

The primary model used in this baseline is **Elastic Net regression**, which combines:

- L1 regularization (Lasso): feature selection and sparsity  
- L2 regularization (Ridge): numerical stability and multicollinearity control  

#### Why Elastic Net?

Elastic Net was selected because it:
- Handles correlated features gracefully.
- Produces interpretable coefficients.
- Provides a smooth transition between sparse and dense solutions.
- Is well-suited for high-dimensional biological data.

This makes it ideal as a **first-pass global model**.

---

## Training Strategy

- The dataset is split into training and test sets using a fixed random seed.
- Hyperparameters are selected using cross-validation on the training set.
- No manual tuning is performed beyond reasonable defaults.

This ensures:
- Reproducibility
- Minimal researcher bias
- Honest generalization estimates

---

## Evaluation Metrics

Model performance is assessed using standard regression metrics, including:

- Coefficient of determination (R²)
- Error-based metrics (e.g. MSE / RMSE where applicable)

These metrics are interpreted **comparatively**, not in isolation.

The emphasis is on:
- Consistency across folds
- Gap between training and test performance
- Stability of coefficients

---

## Results Summary

The global baseline demonstrates that:

- A non-trivial fraction of the target variance can be captured using a linear, regularized model.
- Predictive performance is moderate, indicating the presence of signal but also structural complexity.
- Coefficients are generally small and distributed, suggesting no single dominant driver at the global level.

This outcome is expected and desirable for a baseline model.

---

## Interpretation

Key takeaways from this baseline:

- The problem is **not trivially linear**, but also not purely random.
- Global patterns exist, but are likely diluted by heterogeneity.
- More expressive models or stratified approaches may capture additional signal.

Importantly, the baseline confirms that:
> Any future improvement must outperform a strong, well-regularized linear reference.

---

## Limitations

This baseline intentionally does **not**:

- Model non-linear interactions.
- Account for subgroup-specific effects.
- Incorporate domain-driven feature engineering.
- Optimize aggressively for performance.

These limitations define the **scope**, not a weakness.

---

## Role in the Project

This module serves as:

- A sanity check
- A reproducible benchmark
- A reference point for model complexity justification

All downstream models (e.g. non-linear, cell-specific, compound-specific, or hierarchical models) should be evaluated relative to this baseline.

---

## Reproducibility

- All steps are deterministic given the random seed.
- Results can be regenerated end-to-end.
- No external dependencies beyond standard scientific Python libraries.

This ensures long-term maintainability and auditability of the modeling process.
