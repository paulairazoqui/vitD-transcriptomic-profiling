# Global ML Baseline and Exploratory Feature Support

## Overview

This notebook provides a **global machine learning baseline** for the project and a lightweight bridge to future modeling work.
It is intentionally practical and conservative: it tests simple predictive structure across all signatures, then exports reusable score/feature artifacts for downstream statistical and biological follow-up.

This notebook currently includes three implemented components:

1. **PCA + LogisticRegression classification baseline** for dose-bin discrimination.
2. **Minimal core-score-only LogisticRegression baseline** using a single biologically informed feature (`core_score`).
3. **ElasticNet regression on `core_score`** to extract stable candidate genes for future modeling support.

---

## Inputs

Primary notebook inputs are:

- `data/exports/expression_matrix_clean.parquet` (gene expression matrix).
- `data/exports/signature_metadata_clean.csv` (signature-level metadata).
- `data/raw_data/geneinfo_beta.txt` (gene metadata used to annotate ElasticNet-selected genes).

The notebook aligns expression columns and metadata rows by `sig_id` and checks required metadata columns such as `cell_id` and `pert_dose`.

---

## Implemented Baseline Components

## 1) PCA + LogisticRegression baseline (global dose-bin classification)

- Builds a binary dose label (`dose_bin`) using within-cell-line median split when needed.
- Uses PCA-reduced gene-expression features plus L2-regularized logistic regression.
- Evaluates with group-aware cross-validation by cell line to reduce leakage across biological contexts.

This component is an **exploratory reference baseline**, not a final predictive endpoint.

## 2) Core-score-only LogisticRegression baseline

- Computes/uses `core_score` as a single feature.
- Fits a minimal logistic regression baseline with group-aware validation.

This serves as a compact benchmark for how much signal is captured by the core score alone.

## 3) ElasticNet regression for core-score-related feature extraction

- Regresses `core_score` on transcriptome-wide features with ElasticNet and cross-validated hyperparameters.
- Aggregates coefficient stability information across folds/runs.
- Annotates selected genes with gene metadata for interpretability.

Selected genes are best interpreted as **candidate features associated with the modeled response**, not validated biological mechanisms.

---

## Outputs

This notebook writes:

- `data/exports/signature_metadata_with_core_score.csv` (metadata augmented with computed `core_score`).
- `data/exports/stable_genes_elasticnet_core_score.csv` (ElasticNet-derived stable gene candidates, annotated where possible).

---

## Interpretation and Project Role

- Reported baseline performance is **exploratory/supportive** and should be interpreted as reference-level evidence of learnable structure.
- The exported stable genes are **feature candidates** for follow-up modeling and functional context, not stand-alone mechanistic proof.
- Overall, this notebook provides a **reference baseline for future modeling** (e.g., richer statistical models, stratified analyses, or non-linear methods) and reusable artifacts for downstream steps.

---

## Limitations

Current scope intentionally does not establish causal claims, definitive mechanistic ranking, or optimized production-grade predictors.
Its purpose is baseline calibration plus candidate feature generation under transparent, reproducible assumptions.
