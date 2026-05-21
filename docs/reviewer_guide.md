# Reviewer guide

This page provides a concise navigation aid for reviewers, collaborators, and future readers evaluating manuscript-associated workflows and surrounding repository context.

## 1) Repository overview

This repository contains:
- manuscript-associated workflows used for manuscript-linked analyses and outputs
- exploratory/supporting analyses retained for broader research context
- validation and robustness workflows for sensitivity and stability checks
- deprecated/provenance notebooks retained for auditability and historical traceability
- backend/dashboard infrastructure and related support materials

For formal manuscript framing and boundaries, see [`docs/PAPER_CONTEXT.md`](PAPER_CONTEXT.md). For full notebook-level classification, see [`docs/notebook_index.md`](notebook_index.md).

## 2) Recommended reading order

1. [`README.md`](../README.md)
2. [`docs/PAPER_CONTEXT.md`](PAPER_CONTEXT.md)
3. [`docs/notebook_index.md`](notebook_index.md)
4. [`docs/reviewer_guide.md`](reviewer_guide.md)

## 3) Minimal manuscript-associated workflow

For a minimal manuscript-associated navigation path, start with:

`notebooks/01_filtering.ipynb`  
→ `notebooks/02_EDA.ipynb`  
→ `notebooks/03_EDA_subset.ipynb`  
→ `notebooks/04_directed_results.ipynb`  
→ `notebooks/07_statistical_modeling_core_score.ipynb`

This sequence is an orienting path for external review of the central manuscript workflow. See [`docs/notebook_index.md`](notebook_index.md) for notebook classifications and roles.

## 4) Non-canonical notebooks and directories

The following are supportive/exploratory/provenance layers and should not be interpreted as canonical manuscript-regeneration entry points:
- `notebooks/05_ml_baseline_global.ipynb`
- `notebooks/04_sensitivity_core_score_robustness.ipynb`
- `enrichment/analysis.ipynb`
- `notebooks/deprecated/`

Their value is in context, validation/robustness support, exploratory extension, or historical traceability, as classified in [`docs/notebook_index.md`](notebook_index.md).

## 5) Artifact guidance

Major reusable artifacts are documented in existing repository docs, including:
- expression matrix exports
- signature metadata exports
- sensitivity artifacts

Use:
- [`data/exports/README_exports.md`](../data/exports/README_exports.md)
- [`results/sensitivity/README.md`](../results/sensitivity/README.md)
- notebook-specific documentation pages linked from [`docs/notebook_index.md`](notebook_index.md)

## 6) Reproducibility expectations

- CI validates lightweight repository integrity checks only.
- Notebook execution is not performed in CI.
- Some exploratory/supporting workflows may depend on locally available artifacts or resources.
- Deprecated/provenance notebooks are retained for auditability and historical context, not as active execution workflows.

## 7) Reviewer guidance

- Focus first on the manuscript-associated notebook path and related manuscript outputs.
- Safely defer exploratory, robustness/supporting, and deprecated/provenance layers on an initial pass unless those questions are in scope.
- Interpret taxonomy distinctions as workflow-role boundaries (manuscript, robustness/validation, exploratory/supporting, backend/dashboard, deprecated/provenance), not as changes to manuscript scientific claims.
