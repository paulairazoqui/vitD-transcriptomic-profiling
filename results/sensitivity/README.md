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

Do not delete these yet. `notebooks/04_sensitivity_core_score_robustness.ipynb` is now the preferred notebook for read-only robustness validation, while `notebooks/overlap_confirmation.ipynb` is retained for historical/provenance reference only. Historical notebook-root artifacts must remain in place until the migration is fully complete.

## Planned migration of overlap confirmation checks

`notebooks/overlap_confirmation.ipynb` is retained as a historical/provenance validation notebook and still reads historical notebook-root artifacts directly. Useful checks to migrate into `notebooks/04_sensitivity_core_score_robustness.ipynb` include precomputed top30/top50/top100 core-score correlations, gene-set overlap counts and retained fractions, and artifact existence/schema checks. Full recomputation from expression/metadata should remain future optional work behind an explicit disabled-by-default regeneration flag.

No-delete policy: keep these historical files until migration is complete: `notebooks/core_scores_top30.csv`, `notebooks/core_scores_top50.csv`, `notebooks/core_scores_top100.csv`, `notebooks/core_v2.pkl`, `notebooks/core_v3.pkl`, `notebooks/core_v2_top30.pkl`, and `notebooks/core_v2_top100.pkl`. Namespaced top30 and top100 CSVs already exist under `results/sensitivity/` and should be preferred for future robustness checks. Historical artifacts should not be deleted or moved until the consolidated scaffold reproduces the useful checks.

## Future consolidation

Future consolidation should continue in `notebooks/04_sensitivity_core_score_robustness.ipynb` as a validation-only, namespaced scaffold. Any regeneration capability should remain optional, explicit, and disabled by default, and the scaffold should not write to canonical manuscript output paths.
