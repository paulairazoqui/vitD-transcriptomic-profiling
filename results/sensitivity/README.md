# Sensitivity and robustness artifacts

Artifacts under `results/sensitivity/` are derived, versioned sensitivity artifacts. They are not raw data. These files support robustness checks and manuscript supplementary analyses while remaining separated from canonical manuscript outputs.

| Artifact path | Variant / threshold | Role | Consumed by | Source/provenance | Status |
| --- | --- | --- | --- | --- | --- |
| `results/sensitivity/top30/core_scores_top30.csv` | Top-30 core-window robustness artifact | Supports core-score sensitivity and robustness checks | Canonical Supplementary Figure S3 robustness section in `notebooks/04_directed_results.ipynb` and the robustness scaffold in `notebooks/04_sensitivity_core_score_robustness.ipynb` | Copied unchanged from historical notebook-root artifact | Versioned sensitivity artifact |
| `results/sensitivity/top100/core_scores_top100.csv` | Top-100 core-window robustness artifact | Supports core-score sensitivity and robustness checks | Canonical Supplementary Figure S3 robustness section in `notebooks/04_directed_results.ipynb` and the robustness scaffold in `notebooks/04_sensitivity_core_score_robustness.ipynb` | Copied unchanged from historical notebook-root artifact | Versioned sensitivity artifact |

## Historical notebook-root archive

Historical notebook-root artifacts have been moved unchanged out of `notebooks/` and into `results/sensitivity/historical/notebook_root/` for provenance:

- `results/sensitivity/historical/notebook_root/core_scores_top30.csv`
- `results/sensitivity/historical/notebook_root/core_scores_top50.csv`
- `results/sensitivity/historical/notebook_root/core_scores_top100.csv`
- `results/sensitivity/historical/notebook_root/core_v2.pkl`
- `results/sensitivity/historical/notebook_root/core_v3.pkl`
- `results/sensitivity/historical/notebook_root/core_v2_top30.pkl`
- `results/sensitivity/historical/notebook_root/core_v2_top100.pkl`

Do not delete or rewrite these files. They are provenance artifacts used by `notebooks/04_sensitivity_core_score_robustness.ipynb` as read-only historical fallbacks and by deprecated provenance notebooks under `notebooks/deprecated/` when historical review is needed.

## Deprecated notebook provenance

Deprecated directed-results variants and overlap-confirmation history are retained under `notebooks/deprecated/`:

- `notebooks/deprecated/04_directed_results_plus3.ipynb`
- `notebooks/deprecated/04_directed_results_top30.ipynb`
- `notebooks/deprecated/overlap_confirmation.ipynb`

Current robustness/sensitivity validation should use `notebooks/04_sensitivity_core_score_robustness.ipynb`. The deprecated notebooks are historical/provenance records only and should not be treated as current validation entry points or manuscript-regeneration sources.

## Future consolidation

Future consolidation should continue in `notebooks/04_sensitivity_core_score_robustness.ipynb` as a validation-only, namespaced scaffold. Any regeneration capability should remain optional, explicit, and disabled by default, and the scaffold should not write to canonical manuscript output paths.
