# Notebook index

This repository keeps the manuscript-associated analysis workflow alongside broader exploratory, validation, and support notebooks. The main manuscript track is organized around the numbered notebooks in `notebooks/`: dataset definition (`01`), exploratory quality/structure checks (`02`–`03`), directed result generation (`04`), functional interpretation (`06`), and statistical modeling (`07`). Additional notebooks are retained to document sensitivity checks, validation steps, dashboard/database support, or exploratory development work; they are not all required to reproduce the manuscript-associated results.

## Five-track taxonomy

This repository is framed as a **manuscript + vitamin D transcriptomics research platform**. Notebooks and related materials are organized into five active tracks:

1. **Manuscript track** — notebooks and artifacts used to regenerate manuscript-associated analyses.
2. **Robustness/validation track** — sensitivity checks and validation-focused analyses that test the stability and context of findings.
3. **Exploratory/future analyses** — hypothesis-generation and forward-looking analyses that support ongoing research extension.
4. **Dashboard/backend support** — notebook outputs and infrastructure-oriented analyses that feed dashboard/database workflows and operational research support.
5. **Deprecated/provenance** — historically important records and prior variants maintained for provenance, interpretability, and auditability (not deletion candidates, and not active workflows).

All five tracks are maintained as meaningful parts of the broader platform. Manuscript, robustness/validation, exploratory/future, and backend/dashboard tracks support active research/infrastructure workflows, while deprecated/provenance materials are preserved as maintained provenance and audit records rather than deletion candidates.

## Terminology note

- **manuscript-associated** = belongs to the manuscript evidentiary pipeline context.
- **canonical** = authoritative manuscript-regeneration source/path, not merely “important.”
- **supporting** = contributes context, validation, interpretation, infrastructure, or future-development value but is not itself a canonical manuscript-regeneration entry point.
- **validation** = consistency/integrity checks.
- **robustness** = stability under alternative settings/artifacts.
- **deprecated/provenance** = retained historical records for auditability, not active workflows.
- **workflow** = use a qualifying prefix where ambiguity exists (for example, manuscript workflow, validation workflow, backend operational workflow).

## Notebook classification

| notebook | category | purpose | manuscript relation | primary outputs/results | documentation page |
|---|---|---|---|---|---|
| `notebooks/01_filtering.ipynb` | manuscript-associated | Defines the curated LINCS vitamin D subset and exports filtered metadata/expression inputs for downstream analysis. | canonical | Processed signature metadata, selected signature IDs, and vitamin D expression matrix under `data/processed_data/`. | [01 filtering documentation](notebooks/01_filtering_documentation.md) |
| `notebooks/02_EDA.ipynb` | manuscript-associated | Explores annotation structure, expression patterns, recurrence, and candidate response summaries in the vitamin D signature set. | manuscript-associated | Exploratory figures for manuscript/supplementary use plus dashboard summary exports under `data/dashboard/`. | [02 EDA documentation](notebooks/02_EDA_documentation.md) |
| `notebooks/03_EDA_subset.ipynb` | manuscript-associated | Cleans/aligns the curated subset, checks coverage and global structure, and creates the clean analysis-ready exports. | canonical | PCA/scree figures, PERMANOVA support tables, `data/exports/expression_matrix_clean.parquet`, and `data/exports/signature_metadata_clean.csv`. | [03 EDA subset documentation](notebooks/03_EDA_subset_documentation.md) |
| `notebooks/04_directed_results.ipynb` | manuscript-associated | Runs the primary directed analyses: consensus core definition, `core_score`, dose-response summaries, pathway enrichment, and manuscript figure generation. | canonical | Core gene/score files, dose-response tables, enrichment/preranked outputs, and manuscript figures under `results/`. | [04 directed results documentation](notebooks/04_directed_results_documentation.md) |
| `notebooks/deprecated/04_directed_results_plus3.ipynb` | deprecated sensitivity/variant provenance | Variant of the directed-results workflow retained to compare alternative directed-analysis settings. | deprecated/provenance | Alternative core/dose-response/enrichment summaries and figures, used as workflow context rather than the primary manuscript path. | [deprecated 04 plus3 documentation](notebooks/deprecated_04_directed_results_plus3_documentation.md) |
| `notebooks/deprecated/04_directed_results_top30.ipynb` | deprecated sensitivity/variant provenance | Directed-results variant using a top-30 core-size setting for robustness/sensitivity comparison. | deprecated/provenance | Top-30 core score artifacts and comparable directed-analysis summaries/figures. | [deprecated 04 top30 documentation](notebooks/deprecated_04_directed_results_top30_documentation.md) |
| `notebooks/04_sensitivity_core_score_robustness.ipynb` | robustness/validation | Primary notebook for read-only robustness/sensitivity validation; validation-oriented, namespaced artifact aware, and the intended consolidation target for historical overlap/sensitivity checks. It is not part of the canonical manuscript-regeneration workflow. | manuscript-associated | Validates namespaced sensitivity artifacts under `results/sensitivity/`; no manuscript figure generation or artifact regeneration by default. | [04 sensitivity robustness documentation](notebooks/04_sensitivity_core_score_robustness_documentation.md) |
| `notebooks/05_ml_baseline_global.ipynb` | exploratory/development | Trains an interpretable global Elastic Net baseline as a modeling sanity check and feature-selection reference. | exploratory/future | `signature_metadata_with_core_score.csv` and `stable_genes_elasticnet_core_score.csv` exports under `data/exports/`. | [05 ML baseline documentation](notebooks/05_ml_baseline_global_documentation.md) |
| `notebooks/06_functional_context.ipynb` | manuscript-associated | Adds functional context for selected/stable genes and upstream enrichment results without redefining the core analyses. | manuscript-associated | Functional-context export of stable gene symbols under `data/exports/functional_context/` and interpretation notes. | [06 functional context documentation](notebooks/06_functional_context_documentation.md) |
| `notebooks/07_statistical_modeling_core_score.ipynb` | manuscript-associated | Models `core_score` associations with dose and cellular context to provide formal statistical support for directed results. | canonical | Statistical model summaries and dose-response interpretation in notebook outputs. | [07 statistical modeling documentation](notebooks/07_statistical_modeling_core_score_documentation.md) |
| `notebooks/deprecated/overlap_confirmation.ipynb` | deprecated historical/provenance-only | Deprecated for current validation workflows; retained for provenance after historical overlap checks were consolidated into `notebooks/04_sensitivity_core_score_robustness.ipynb`. | deprecated/provenance | Historical overlap counts, retained fractions, and score-correlation checks in notebook outputs; not a current validation entry point. | [deprecated overlap confirmation documentation](notebooks/deprecated_overlap_confirmation_documentation.md) |
| `enrichment/analysis.ipynb` | supporting validation | Examines external VDR ChIP-seq/GEO resources for overlap-style context around VDR-related analyses. | supporting | VDR-overlap exploratory results in notebook outputs; retained as supporting workflow context. | [enrichment analysis documentation](notebooks/enrichment_analysis_documentation.md) |

### Related governance/provenance docs

The files below are maintained for governance/provenance context and planning; they are **not** direct one-to-one notebook companion pages:

- [`docs/notebooks/04_helper_extraction_plan.md`](notebooks/04_helper_extraction_plan.md)
- [`docs/notebooks/04_directed_results_variants.md`](notebooks/04_directed_results_variants.md)

## Reproduction guidance

For manuscript-associated reproduction, start with the numbered workflow in `notebooks/` and prioritize `01_filtering.ipynb`, `02_EDA.ipynb`, `03_EDA_subset.ipynb`, `04_directed_results.ipynb`, `06_functional_context.ipynb`, and `07_statistical_modeling_core_score.ipynb`. The robustness/validation, exploratory/future, and backend/dashboard support tracks remain active components of the full platform framing and should be used whenever those objectives are in scope. Deprecated/provenance materials are maintained as provenance/audit records for historical traceability and contextual review.
