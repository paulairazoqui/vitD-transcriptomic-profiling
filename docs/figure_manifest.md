# Figure manifest

This manifest records the finalized manuscript figure tree. Manuscript and supplementary figure assets under `results/figures/paper/` are SVG-only; no PNG or PDF files are part of the paper figure hierarchy.

## Organization summary

- `results/figures/paper/` contains exactly 18 tracked SVG files.
- Main manuscript figures are grouped under `figure_1/` through `figure_6/`.
- Supplementary manuscript figures are grouped under `supplementary/`.
- Dashboard artifacts are stored outside the static manuscript figure tree under `data/dashboard/` and `results/dashboard/`.

## Manuscript-associated figure mapping

| Manuscript figure/panel | Canonical SVG path | Output type | Notes |
|---|---|---|---|
| Figure 1A and Figure 1B | `results/figures/paper/figure_1/figure_1AB_pca.svg` | Main figure | Combined PCA figure. |
| Figure 1C | `results/figures/paper/figure_1/figure_1C_pca_scree_plot.svg` | Main figure | PCA scree plot. |
| Figure 2A | `results/figures/paper/figure_2/figure_2A_top_genes_modulated.svg` | Main figure | Top modulated genes. |
| Figure 2B | `results/figures/paper/figure_2/figure_2B_heatmap_expression.svg` | Main figure | Expression heatmap. |
| Figure 3A | `results/figures/paper/figure_3/figure_3A_hallmark_enrichment.svg` | Main figure | Hallmark enrichment. |
| Figure 3B | `results/figures/paper/figure_3/figure_3B_consensus_hallmarks.svg` | Main figure | Consensus hallmarks. |
| Figure 3C | `results/figures/paper/figure_3/figure_3C_gene_level_effects.svg` | Main figure | Gene-level effects. |
| Figure 4 | `results/figures/paper/figure_4/Figure_4_forest_dose_response_by_cell.svg` | Main figure | Forest dose response by cell. |
| Figure 5A | `results/figures/paper/figure_5/figure_5A_shared_responsive_genes.svg` | Main figure | Shared responsive genes. |
| Figure 5B | `results/figures/paper/figure_5/figure_5B_shared_responsive_genes.svg` | Main figure | Shared responsive genes. |
| Figure 5C | `results/figures/paper/figure_5/figure_5C_hallmark_enrichment_patterns.svg` | Main figure | Hallmark enrichment patterns. |
| Figure 6 | `results/figures/paper/figure_6/figure_6_VDR-axis_gene_expression_changes.svg` | Main figure | VDR-axis gene expression changes. |

## Supplementary manuscript figure mapping

| Supplementary figure/output | Canonical SVG path | Output type | Notes |
|---|---|---|---|
| Supplementary gene recurrence | `results/figures/paper/supplementary/figure_S1_gene_recurrence.svg` | Supplementary figure | Gene recurrence. |
| Supplementary top 100 gene heatmap | `results/figures/paper/supplementary/figure_supplementary_heatmap_top_100_genes.svg` | Supplementary figure | Top 100 gene heatmap. |
| Supplementary forest dose by compound | `results/figures/paper/supplementary/supp_forest_dose_by_compound.svg` | Supplementary figure | Forest dose response by compound. |
| Supplementary core score by compound | `results/figures/paper/supplementary/supplementary_core_score_by_compound.svg` | Supplementary figure | Core score by compound. |
| Supplementary core score robustness | `results/figures/paper/supplementary/supplementary_core_score_robustness.svg` | Supplementary figure | Core score robustness. |
| Supplementary dose distribution by compound | `results/figures/paper/supplementary/supplementary_dose_distribution_by_compound.svg` | Supplementary figure | Dose distribution by compound. |

## Dashboard outputs

| Output group | File path(s) | Output type | Notes |
|---|---|---|---|
| Dashboard data exports | `data/dashboard/signatures_core.csv`<br>`data/dashboard/compound_summary.csv`<br>`data/dashboard/cluster_summary.csv` | Dashboard | Source tables for dashboard use, distinct from static manuscript figures. |
| Dashboard deliverables | `results/dashboard/dashboard.pbix`<br>`results/dashboard/dashboard.pdf` | Dashboard | Stored outside `results/figures/paper/`. |

## Current figure-tree status

- The paper figure tree is SVG-only for both main manuscript and supplementary assets.
- No PNG or PDF files remain under `results/figures/paper/`.
- No exploratory or development figures are currently listed as present outside the finalized paper hierarchy.
