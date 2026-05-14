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

These variants document exploratory parameter choices and robustness-development history. They must not be used to regenerate manuscript figures or overwrite manuscript outputs.

## Notebook roles and output cautions

| Notebook | Role | Key parameter difference | Manuscript workflow? | Figure-output behavior | Known output risks |
| --- | --- | --- | --- | --- | --- |
| `notebooks/04_directed_results.ipynb` | Canonical directed-results notebook for manuscript analyses and manuscript figure generation. | Uses the canonical manuscript core-gene and scoring parameters (top_n=50, min_votes=2, target_up=42, target_dn=35). | Yes | May write canonical manuscript figures and tables according to the manuscript figure/output workflow. | Canonical robustness sections may depend on externally generated variant core-score files; ensure those inputs are intentionally supplied and versioned before rerunning robustness panels. |
| `notebooks/04_directed_results_plus3.ipynb` | Strict-core sensitivity/development variant retained for provenance. | Uses a stricter core definition/development parameterization than the canonical notebook. | No | Must not write to canonical manuscript output paths; any figure or table exports should be variant-namespaced or disabled before execution. | Duplicated downstream logic, possible table/checkpoint writes, and possible non-namespaced outputs if rerun without cleanup. |
| `notebooks/04_directed_results_top30.ipynb` | Top-30 core-window sensitivity/development variant retained for provenance. | Uses a top-30 core-window sensitivity/development parameterization rather than the canonical manuscript core window. | No | Must not write to canonical manuscript output paths; any figure or table exports should be variant-namespaced or disabled before execution. | Duplicated downstream logic, possible table/checkpoint writes, possible non-namespaced outputs, and a known naming mismatch around `core_v2_top100.pkl`. |

## Usage policy

- Variant notebooks must not be used to regenerate manuscript figures.
- Variants are retained for sensitivity/development provenance only.
- No variant notebook should write to canonical manuscript output paths.
- Before running a variant, review all save/export cells for table writes, checkpoint writes, figure writes, and any path that is not variant-namespaced.
- Variant output files should be explicitly namespaced and separated from canonical manuscript outputs.

## Known risks and follow-up consolidation

The variant notebooks duplicate substantial downstream directed-results logic after changing core-definition parameters. This creates maintenance risk because fixes to manuscript analyses, plotting, table export, or checkpoint handling can diverge across notebooks.

Known risks include:

- duplicated downstream logic;
- possible table/checkpoint writes;
- non-namespaced outputs;
- the `top30` naming mismatch around `core_v2_top100.pkl`;
- canonical robustness sections that depend on externally generated variant core-score files.

These variants should eventually be consolidated into a parameterized sensitivity notebook or shared utilities so that sensitivity settings are explicit inputs rather than copied notebooks. Consolidation should preserve provenance while preventing variant runs from writing to canonical manuscript output paths.
