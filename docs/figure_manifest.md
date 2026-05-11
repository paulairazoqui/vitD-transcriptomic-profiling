# Figure manifest

This manifest documents the relationship between manuscript-associated figure files, other output figures, dashboard artifacts, and the notebooks that appear to generate or support them. It is descriptive only: it does not rename files, move files, revise figure labels, or add scientific interpretation.

## Organization summary

- Manuscript-associated figures are stored under `results/figures/paper/`, grouped by figure directory (`figure_2` through `figure_6`) plus `supplementary/`.
- No `results/figures/paper/figure_1/` directory or obvious Figure 1 output file is present in the repository at the time of this manifest.
- Top-level files in `results/figures/` are retained separately from the `paper/` hierarchy. These appear to be exploratory, supplementary, robustness, or development outputs unless explicitly mirrored into `results/figures/paper/`.
- Dashboard files are stored separately from static figures: source tables are under `data/dashboard/`, and dashboard deliverables are under `results/dashboard/`.
- Notebook-to-output relationships were inferred from saved file paths and output names embedded in notebooks. Where a matching save path was not detected, the generating notebook is listed as not identified.

## Manuscript-associated figure mapping

| Manuscript figure/panel | File path(s) | Generating notebook | Output type | Notes |
|---|---|---|---|---|
| Figure 1 | Not detected | Not identified | Main figure | No `results/figures/paper/figure_1/` directory or obvious `figure_1` output file was detected. |
| Figure 2A | `results/figures/paper/figure_2/figure_2A_pca.png`<br>`results/figures/paper/figure_2/figure_2A_pca.pdf` | `notebooks/03_EDA_subset.ipynb` | Main figure | Manuscript-associated PCA output in the paper figure hierarchy. |
| Figure 2C | `results/figures/paper/figure_2/figure_2C_pca_scree_plot.png`<br>`results/figures/paper/figure_2/figure_2C_pca_scree_plot.pdf` | `notebooks/03_EDA_subset.ipynb` | Main figure | Figure 2B was not detected as a saved output in this repository. |
| Figure 3A | `results/figures/paper/figure_3/figure_3A_top_genes_modulated.png`<br>`results/figures/paper/figure_3/figure_3A_top_genes_modulated.pdf`<br>`results/figures/paper/figure_3/figure_3A_top_genes_modulated.svg` | `notebooks/02_EDA.ipynb` | Main figure | Stored in the paper figure hierarchy. The notebook save calls identify PNG/PDF outputs; SVG is present in the output directory. |
| Figure 3B | `results/figures/paper/figure_3/figure_3B_heatmap_expression.png`<br>`results/figures/paper/figure_3/figure_3B_heatmap_expression.pdf`<br>`results/figures/paper/figure_3/figure_3B_heatmap_expression.svg` | `notebooks/02_EDA.ipynb` | Main figure | Stored in the paper figure hierarchy. The notebook save calls identify PNG/PDF outputs; SVG is present in the output directory. |
| Figure 4C | `results/figures/paper/figure_4/figure_4C_consensus_hallmarks.png`<br>`results/figures/paper/figure_4/figure_4C_consensus_hallmarks.pdf`<br>`results/figures/paper/figure_4/figure_4C_consensus_hallmarks.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Duplicate Figure 4C panel label exists; see the separate Figure 4C row below. Variant notebooks reference the same output filename pattern, so the primary manuscript path should be distinguished from sensitivity/development variants when regenerating outputs. |
| Figure 4C | `results/figures/paper/figure_4/figure_4C_gene_level_effects.png`<br>`results/figures/paper/figure_4/figure_4C_gene_level_effects.pdf`<br>`results/figures/paper/figure_4/figure_4C_gene_level_effects.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Duplicate Figure 4C panel label exists; both Figure 4 outputs use `figure_4C_*` filenames. |
| Figure 5A | `results/figures/paper/figure_5/figure_5A_shared_responsive_genes.png`<br>`results/figures/paper/figure_5/figure_5A_shared_responsive_genes.pdf`<br>`results/figures/paper/figure_5/figure_5A_shared_responsive_genes.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Stored in the paper figure hierarchy. |
| Figure 5B | `results/figures/paper/figure_5/figure_5B_shared_responsive_genes.png`<br>`results/figures/paper/figure_5/figure_5B_shared_responsive_genes.pdf`<br>`results/figures/paper/figure_5/figure_5B_shared_responsive_genes.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Stored in the paper figure hierarchy. |
| Figure 5C | `results/figures/paper/figure_5/figure_5C_hallmark_enrichment_patterns.png`<br>`results/figures/paper/figure_5/figure_5C_hallmark_enrichment_patterns.pdf`<br>`results/figures/paper/figure_5/figure_5C_hallmark_enrichment_patterns.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Stored in the paper figure hierarchy. |
| Figure 6 | `results/figures/paper/figure_6/figure_6_VDR-axis_gene_expression_changes.png`<br>`results/figures/paper/figure_6/figure_6_VDR-axis_gene_expression_changes.pdf`<br>`results/figures/paper/figure_6/figure_6_VDR-axis_gene_expression_changes.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Main figure | Stored in the paper figure hierarchy. Filename uses an uppercase acronym and hyphenated `VDR-axis` segment. |

## Supplementary figure mapping

| Manuscript figure/panel | File path(s) | Generating notebook | Output type | Notes |
|---|---|---|---|---|
| Supplementary Figure S1 | `results/figures/paper/supplementary/figure_S1_gene_recurrence.png`<br>`results/figures/paper/supplementary/figure_S1_gene_recurrence.pdf` | `notebooks/02_EDA.ipynb` | Supplementary | Uses the `figure_S1_*` naming convention. |
| Supplementary heatmap / top 100 genes | `results/figures/paper/supplementary/figure_supplementary_heatmap_top_100_genes.png`<br>`results/figures/paper/supplementary/figure_supplementary_heatmap_top_100_genes.pdf` | `notebooks/02_EDA.ipynb` | Supplementary | Uses a descriptive `figure_supplementary_*` naming convention rather than an `S#` panel label. |
| Supplementary dose response by compound | `results/figures/supp_forest_dose_by_compound.png`<br>`results/figures/supp_forest_dose_by_compound.svg` | `notebooks/04_directed_results.ipynb` | Supplementary / exploratory | Top-level `results/figures/` output, not under `results/figures/paper/supplementary/`. |
| Supplementary dose distribution by compound | `results/figures/supplementary_dose_distribution_by_compound.png`<br>`results/figures/supplementary_dose_distribution_by_compound.svg` | `notebooks/04_directed_results.ipynb` | Supplementary / exploratory | Top-level `results/figures/` output, not under `results/figures/paper/supplementary/`. |
| Supplementary core score robustness | `results/figures/supplementary_core_score_robustness.png`<br>`results/figures/supplementary_core_score_robustness.svg` | `notebooks/04_directed_results.ipynb` | Supplementary / exploratory | Top-level `results/figures/` output, not under `results/figures/paper/supplementary/`. |
| Supplementary core score by compound | `results/figures/supplementary_core_score_by_compound.png`<br>`results/figures/supplementary_core_score_by_compound.svg` | `notebooks/04_directed_results.ipynb` | Supplementary / exploratory | Top-level `results/figures/` output, not under `results/figures/paper/supplementary/`. |
| Supplementary core score by cell line | `results/figures/supplementary_core_score_by_cell_line.png` | Not identified | Supplementary / exploratory | Top-level `results/figures/` output. A matching notebook save path was not detected. |

## Exploratory and development outputs

| Manuscript figure/panel | File path(s) | Generating notebook | Output type | Notes |
|---|---|---|---|---|
| Exploratory core score distribution | `results/figures/box_strip_core_scores.png` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Exploratory / development | Top-level figure output, separate from the paper hierarchy. |
| Exploratory forest slopes | `results/figures/forest_slopes.png` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Exploratory / development | Top-level figure output, separate from the paper hierarchy. |
| Exploratory forest dose response by cell | `results/figures/forest_dose_response_by_cell.png`<br>`results/figures/forest_dose_response_by_cell.svg` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Exploratory / development | Top-level figure output, separate from the paper hierarchy. |
| Exploratory Hallmarks dotplot by cell | `results/figures/dotplot_hallmarks_by_cell.png` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Exploratory / development | Top-level figure output generated by dynamic `dotplot_{library}_by_cell` naming. |
| Exploratory Reactome dotplot by cell | `results/figures/dotplot_reactome_by_cell.png` | `notebooks/04_directed_results.ipynb`; also referenced by variant notebooks `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` | Exploratory / development | Top-level figure output generated by dynamic `dotplot_{library}_by_cell` naming. |
| Exploratory cell Hallmarks dotplot | `results/figures/dotplot_cell_Hallmarks.png`<br>`results/figures/dotplot_cell_Hallmarks.svg` | Not identified | Exploratory / development | Top-level output with a different naming pattern from `dotplot_hallmarks_by_cell.png`; no matching save path was detected. |
| Exploratory cell Reactome dotplot | `results/figures/dotplot_cell_Reactome.png`<br>`results/figures/dotplot_cell_Reactome.svg` | Not identified | Exploratory / development | Top-level output with a different naming pattern from `dotplot_reactome_by_cell.png`; no matching save path was detected. |

## Dashboard outputs

| Manuscript figure/panel | File path(s) | Generating notebook | Output type | Notes |
|---|---|---|---|---|
| Dashboard data exports | `data/dashboard/signatures_core.csv`<br>`data/dashboard/compound_summary.csv`<br>`data/dashboard/cluster_summary.csv` | `notebooks/02_EDA.ipynb` | Dashboard | Source tables for dashboard use, distinct from static manuscript figures. |
| Dashboard deliverables | `results/dashboard/dashboard.pbix`<br>`results/dashboard/dashboard.pdf` | Not identified | Dashboard | Stored outside `results/figures/`; no notebook save path was detected for these deliverables. |

## Detected ambiguities and naming inconsistencies

- **Figure 1 not detected:** There is no detected `results/figures/paper/figure_1/` directory or obvious `figure_1` output file.
- **Missing or unrepresented panels:** Figure 2 has detected outputs for panels 2A and 2C, but no detected Figure 2B output file.
- **Duplicated panel labels:** Two separate Figure 4 outputs are labeled as Figure 4C: `figure_4C_consensus_hallmarks.*` and `figure_4C_gene_level_effects.*`.
- **Mixed supplementary naming conventions:** Supplementary files use multiple patterns, including `figure_S1_*`, `figure_supplementary_*`, `supp_*`, and `supplementary_*`.
- **Mixed supplementary locations:** Some supplementary-associated outputs are under `results/figures/paper/supplementary/`, while others are top-level files under `results/figures/`.
- **Top-level exploratory outputs:** Files directly under `results/figures/` are not assumed to be manuscript main figures unless they are also represented in the `results/figures/paper/` hierarchy or explicitly identified by notebook context.
- **Variant notebooks share output names:** `notebooks/04_directed_results_plus3.ipynb` and `notebooks/04_directed_results_top30.ipynb` reference several of the same figure filename patterns as `notebooks/04_directed_results.ipynb`, so rerunning variants may overwrite or reproduce similarly named outputs unless run in a controlled workflow.
