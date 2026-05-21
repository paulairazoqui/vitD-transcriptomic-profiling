# Notebook Documentation: `notebooks/04_sensitivity_core_score_robustness.ipynb`

## Documented Notebook Path
`notebooks/04_sensitivity_core_score_robustness.ipynb`

## Five-Track Role
**Track:** Validation and robustness support for directed analyses (manuscript-associated, non-canonical).

## Status
**Active support notebook** for robustness checks.

## Purpose
Validate that previously generated core-score sensitivity results remain internally consistent across existing artifact namespaces and historical variants.

## Main Inputs
- Existing, already-generated directed-analysis and sensitivity artifacts.
- Preferred namespaced sensitivity outputs (for example variant-scoped artifacts such as top30/top50/top100 when present in the active namespace).
- Historical fallback artifacts used only when preferred namespaced resources are unavailable.
- Associated metadata required to align provenance and compare stored results consistently.

## Main Outputs / Artifacts
- Read-only comparison summaries of agreement/disagreement across existing sensitivity artifacts.
- Diagnostic views highlighting where prior conclusions are stable versus sensitivity-dependent.

## What the Notebook Does
- Loads and inspects existing robustness/sensitivity outputs rather than serving as a regeneration workflow.
- Applies provenance-aware loading logic, prioritizing current namespaced artifacts and then falling back to historical equivalents when necessary.
- Compares previously produced variant results (for example, top30/top50/top100 where applicable).
- Runs validation checks across variants (alignment, overlap, directionality/score consistency as implemented) to identify agreement versus drift.
- Reports consistency patterns for interpretation support.

## Artifact Consistency Expectations
- Preferred behavior is cross-variant consistency for core directional conclusions.
- Minor numeric variation across historical and namespaced artifacts can occur and is interpreted in context.
- Substantial discordance is treated as a robustness warning that should be surfaced to directed-analysis interpretation rather than silently ignored.

## Why It Exists
Provide an auditable validation layer so confidence in core-score conclusions is based on cross-artifact consistency, not a single archived result set.

## How to Interpret Outputs
- Treat cross-variant agreement as **robustness support** for existing findings.
- Treat mismatches as **caution flags** indicating sensitivity to earlier configuration choices or artifact lineage.

## Repository Fit
Sits beside directed-analysis materials as **read-only validation support** over existing artifacts and historical result namespaces.

## Boundaries and Cautions
- **Not** a canonical manuscript regeneration notebook.
- **Does not modify manuscript outputs** and should not be used to rewrite canonical results.
- Interpretation remains supportive/contextual unless explicitly promoted elsewhere in the repository.
