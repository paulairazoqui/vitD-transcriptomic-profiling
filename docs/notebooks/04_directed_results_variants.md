# Directed-results notebook variants

This document records the role of the redundant directed-results notebooks so that manuscript regeneration uses the correct source notebook while preserving development provenance for sensitivity checks.

## Canonical manuscript notebook

The canonical manuscript workflow is:

- `notebooks/04_directed_results.ipynb`

Use this notebook for manuscript-directed results and manuscript figure generation. It is the only directed-results notebook in this group that should be treated as a manuscript-regeneration source.

## Variant notebooks

Two directed-results variants are retained for sensitivity and development provenance:

- `notebooks/04_directed_results_plus3.ipynb` — strict-core sensitivity/development variant.
- `notebooks/04_directed_results_top30.ipynb` — top-30 core-window sensitivity/development variant.

These variants document exploratory parameter choices and robustness-development history. They must not be used to regenerate manuscript figures or overwrite manuscript outputs. Their controlled outputs are now routed to variant-specific directories under `results/sensitivity/plus3/` and `results/sensitivity/top30/`.

Current robustness/sensitivity validation should use `notebooks/04_sensitivity_core_score_robustness.ipynb`. That scaffold performs validation-only checks against retained, namespaced artifacts and does not regenerate manuscript outputs by default. `notebooks/overlap_confirmation.ipynb` is retained only for provenance/history, and the directed-results variants remain provenance/development artifacts rather than current validation entry points.

## Notebook roles and output cautions

| Notebook | Role | Key parameter difference | Manuscript workflow? | Figure-output behavior | Known output risks |
| --- | --- | --- | --- | --- | --- |
| `notebooks/04_directed_results.ipynb` | Canonical directed-results notebook for manuscript analyses and manuscript figure generation. | Uses the canonical manuscript core-gene and scoring parameters (top_n=50, min_votes=2, target_up=42, target_dn=35). | Yes | May write canonical manuscript figures and tables according to the manuscript figure/output workflow. | Canonical robustness sections may depend on externally generated variant core-score files; ensure those inputs are intentionally supplied and versioned before rerunning robustness panels. |
| `notebooks/04_directed_results_plus3.ipynb` | Strict-core sensitivity/development variant retained for provenance. | Uses a stricter core definition/development parameterization than the canonical notebook. | No | Must not write to canonical manuscript output paths or regenerate manuscript figures; controlled variant outputs are routed to `results/sensitivity/plus3/`. | Mitigated: controlled outputs are variant-namespaced under `results/sensitivity/plus3/`. Remaining: duplicated downstream logic and possible maintenance drift. |
| `notebooks/04_directed_results_top30.ipynb` | Top-30 core-window sensitivity/development variant retained for provenance. | Uses a top-30 core-window sensitivity/development parameterization rather than the canonical manuscript core window. | No | Must not write to canonical manuscript output paths or regenerate manuscript figures; controlled variant outputs are routed to `results/sensitivity/top30/`. | Mitigated: controlled outputs are variant-namespaced under `results/sensitivity/top30/`. Remaining: duplicated downstream logic, possible maintenance drift, and the known naming mismatch around `core_v2_top100.pkl` if still present. |

## Usage policy

- Variant notebooks must not be used to regenerate manuscript figures.
- Variants are retained for sensitivity/development provenance only.
- No variant notebook should write to canonical manuscript output paths.
- Variant-controlled outputs are routed to variant-specific directories: `results/sensitivity/plus3/` for the plus3 variant and `results/sensitivity/top30/` for the top30 variant.
- Before running a variant, review all save/export cells for table writes, checkpoint writes, figure writes, and any path that is not variant-namespaced.
- Any future output added to a variant must remain variant-namespaced and separated from canonical manuscript outputs.

## Canonical robustness sensitivity artifacts

Namespaced sensitivity artifacts now provide the robustness inputs consumed by the canonical notebook's robustness / Supplementary Figure S3 section:

- `results/sensitivity/top30/core_scores_top30.csv`
- `results/sensitivity/top100/core_scores_top100.csv`

These CSVs are versioned sensitivity artifacts copied unchanged from historical notebook-root artifacts. They are not raw data. Going forward, the namespaced files under `results/sensitivity/` are the preferred sources for canonical robustness reruns; historical notebook-root copies are retained only for provenance and should not be treated as preferred inputs.

## Known risks and follow-up consolidation

The variant notebooks duplicate substantial downstream directed-results logic after changing core-definition parameters. This creates maintenance risk because fixes to manuscript analyses, plotting, table export, or checkpoint handling can diverge across notebooks.

Mitigated risks:

- controlled variant outputs are now routed to variant-specific directories (`results/sensitivity/plus3/` and `results/sensitivity/top30/`), reducing the risk that intended variant outputs overwrite canonical manuscript outputs.

Remaining risks include:

- duplicated downstream logic;
- maintenance drift between the canonical notebook and retained variants;
- any newly added variant output that is not kept variant-namespaced;
- the `top30` naming mismatch around `core_v2_top100.pkl`, if still present;
- canonical robustness sections that depend on externally generated variant core-score files, if still applicable.

These variants should eventually be consolidated into a parameterized sensitivity notebook or shared utilities so that sensitivity settings are explicit inputs rather than copied notebooks. Consolidation should preserve provenance while preventing variant runs from writing to canonical manuscript output paths.
