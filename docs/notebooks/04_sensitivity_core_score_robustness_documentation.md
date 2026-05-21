# Notebook Documentation: `notebooks/04_sensitivity_core_score_robustness.ipynb`

## Documented Notebook Path
`notebooks/04_sensitivity_core_score_robustness.ipynb`

## Five-Track Role
**Track:** Validation and sensitivity support for directed analyses (non-canonical).

## Status
**Active support notebook** for robustness checks.

## Purpose
Validate that previously generated core-score sensitivity results remain internally consistent across existing artifact namespaces and historical variants.

## Main Inputs
- Existing, already-generated directed-analysis and sensitivity artifacts.
- Namespaced/historical outputs for sensitivity variants such as top30/top50/top100 (where present).
- Associated metadata needed to align and compare those stored artifacts.

## Main Outputs / Artifacts
- Read-only comparison summaries of agreement/disagreement across existing sensitivity artifacts.
- Diagnostic views highlighting where prior conclusions are stable versus sensitivity-dependent.

## What the Notebook Does
- Loads and inspects existing robustness/sensitivity outputs rather than serving as a default regeneration workflow.
- Compares previously produced variant results (for example, top30/top50/top100 where applicable).
- Reports consistency patterns for interpretation support.

## Why It Exists
Provide an auditable validation layer so confidence in core-score conclusions is based on cross-artifact consistency, not a single archived result set.

## How to Interpret Outputs
- Treat cross-variant agreement as **robustness support** for existing findings.
- Treat mismatches as **caution flags** indicating sensitivity to earlier configuration choices.

## Repository Fit
Sits beside directed-analysis materials as **read-only validation support** over existing artifacts and historical result namespaces.

## Boundaries and Cautions
- **Not** a canonical manuscript regeneration notebook.
- **Does not modify manuscript outputs** and should not be used to rewrite canonical results.
- Interpretation remains supportive/contextual unless explicitly promoted elsewhere in the repository.
