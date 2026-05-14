# Sensitivity and robustness artifacts

Artifacts under `results/sensitivity/` are derived, versioned sensitivity artifacts. They are not raw data. These files support robustness checks and manuscript supplementary analyses while remaining separated from canonical manuscript outputs and historical notebook-root artifacts.

| Artifact path | Variant / threshold | Role | Consumed by | Source/provenance | Status |
| --- | --- | --- | --- | --- | --- |
| `results/sensitivity/top30/core_scores_top30.csv` | Top-30 core-window robustness artifact | Supports core-score sensitivity and robustness checks | Canonical Supplementary Figure S3 robustness section in `notebooks/04_directed_results.ipynb` | Copied unchanged from historical notebook-root artifact | Versioned sensitivity artifact |
| `results/sensitivity/top100/core_scores_top100.csv` | Top-100 core-window robustness artifact | Supports core-score sensitivity and robustness checks | Canonical Supplementary Figure S3 robustness section in `notebooks/04_directed_results.ipynb` | Copied unchanged from historical notebook-root artifact | Versioned sensitivity artifact |

## Historical artifacts

Some historical artifacts still exist under `notebooks/` and are retained for provenance because `notebooks/overlap_confirmation.ipynb` currently reads them directly:

- `notebooks/core_scores_top30.csv`
- `notebooks/core_scores_top50.csv`
- `notebooks/core_scores_top100.csv`
- `notebooks/core_v2.pkl`
- `notebooks/core_v3.pkl`
- `notebooks/core_v2_top30.pkl`
- `notebooks/core_v2_top100.pkl`

Do not delete these yet. Future consolidation should migrate `notebooks/overlap_confirmation.ipynb` to namespaced artifacts or replace it with a consolidated sensitivity notebook.

## Future consolidation

A future consolidated notebook may live at `notebooks/04_sensitivity_core_score_robustness.ipynb`. It should validate and/or regenerate sensitivity artifacts in a parameterized, namespaced way, and it should not write to canonical manuscript output paths.
