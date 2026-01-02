## *Directed Results*
# **Core Analyses of Vitamin D Signatures**

This notebook presents the **directed, hypothesis-driven analyses** of transcriptomic responses to Vitamin D and its analogs.  
Unlike exploratory analyses, here we focus on **predefined questions** (core signatures, dose–response, enrichment) using the modular utilities developed in `vitd_utils`.

All constants, parameters, and paths are centralized in `vitd_utils.config`, ensuring reproducibility and consistency across analyses.

## 2. Gene ID ↔ Symbol Mapping

Most LINCS L1000 resources use **gene IDs** as stable identifiers, while interpretation requires **gene symbols**.  
To ensure consistency, we build a robust mapping between IDs and symbols using `vitd_utils.idsymbols`.  
This step guarantees that downstream analyses (core genes, enrichment, plotting) always have readable gene names with safe fallbacks.

## 3. Consensus Core Genes (definition & scoring)

**Goal.** Define a robust Vitamin D “core” signature (UP/DOWN genes) that recurs across contexts (here: cell lines), and compute a single **core score** per signature capturing the balance of UP vs DOWN core genes.

**Method.**
1) Build a gene × context matrix of effects (here: mean L1000 z-scores **per cell line**).
2) For each context, take the top/bottom `N_TOP` genes and **vote-count** across contexts.
3) Select `CORE_UP_N` / `CORE_DN_N` genes using a minimum vote threshold and deterministic tie-breakers (mean |effect|).
4) Compute **core_score** for every signature:  
   `core_score = mean(z(core_UP)) − mean(z(core_DN))` (column-wise centering).

All thresholds and sizes are centralized in `vitd_utils.config`.

## 4. Dose–Response Analysis

**Goal.** Test whether Vitamin D analogs induce a monotonic transcriptomic response as dose increases, and quantify effect sizes (slopes).

**Method.**
1. Bin doses into "low" vs "high" categories for exploratory plots (`dose.binarize_dose`).
2. Test monotonicity with **Spearman correlation** (`dose.dose_monotonicity`).
3. Estimate slopes with **OLS regression** on log10(dose) (`dose.ols_hc3`) using HC3 robust errors.
4. Summarize slopes across cell lines and visualize with **forest plots** (`plotting.forest_from_models`).

### 4.3 Forest plot — Dose–response slopes (HC3)

We estimate the slope of the dose–response (core_score ~ log10 dose) **per cell line** using OLS with **HC3 robust errors**.  
The forest plot shows the coefficient and its 95% confidence interval (CI); a vertical dashed line at 0 represents “no trend”.  
This complements the monotonicity test by quantifying **effect size** and uncertainty.

### Interpretation — Dose–response slopes (HC3)

Across cell lines, OLS–HC3 slopes for *core_score ~ log10(dose)* are positive and statistically significant in most contexts, indicating a dose-dependent induction of the Vitamin D core response:

- **MCF7**: largest slope, narrow CI, *p* ≪ 1e-6 → strong dose dependence.
- **A549** and **PC3**: clearly positive slopes with tight CIs (***p* < 1e-5**), consistent dose dependence.
- **U2OS**: positive slope with wider CI; still significant (*p* ≈ 0.043), suggesting a weaker but present trend.
- **HA1E**: small slope, CI overlaps zero (*p* ≈ 0.15), indicating limited or context-specific dose dependence.

Overall, these results support a **monotonic, dose-responsive activation** of the Vitamin D core signature in most cell lines, with effect sizes varying by context.

---

## 5.1 Groupwise Spearman correlations (with FDR)

**Goal.** Quantify monotonic dose–response trends by computing **Spearman’s ρ** between `log10(dose)` and `core_score` **within each cell line**.  
**Multiple-testing control.** We report Benjamini–Hochberg **FDR** across cell lines to control the expected false discovery rate.

**Why Spearman?** It is rank-based and robust to non-linearity and mild outliers, complementing OLS–HC3 slope estimates.

## 5.2 Bootstrap CIs for Spearman’s ρ

**Goal.** Quantify uncertainty in the groupwise Spearman correlations using nonparametric **bootstrap** CIs.  
This complements p-values/FDR with effect-size intervals that are robust to non-normality.

### Dose–response monotonicity (Spearman’s ρ)

Groupwise Spearman correlations between *log10(dose)* and *core_score* provided a rank-based assessment of monotonicity:

- **MCF7**, **A549**, and **PC3** showed strong positive correlations (ρ ≈ 0.55–0.63) with narrow bootstrap confidence intervals excluding zero, all highly significant after FDR correction.  
- **U2OS** displayed a weaker but still positive correlation (ρ ≈ 0.32), with wider confidence bounds; significance was retained though effect size was smaller.  
- **HA1E** showed no clear monotonicity (ρ ≈ 0.08), with a CI overlapping zero and non-significant FDR.

Overall, four of the five cell lines exhibited evidence of a dose-dependent monotonic increase in the Vitamin D core signature, with effect sizes again highest in MCF7, A549, and PC3.

## 5.3 Quick OLS slopes (polyfit)

**Goal.** Provide a simple, effect-size–oriented summary of dose–response strength in each cell line.  
We fit a straight line `core_score ~ log10(dose)` using numpy’s `polyfit`, which is fast and stable but does not provide robust errors.  
These slopes complement the HC3 regression (Section 4.3) by offering an easy-to-interpret Δy/Δx metric.

### Interpretation — Quick slopes

MCF7 and A549 exhibit the steepest slopes (~0.45–0.50), indicating strong dose-dependent increases in the Vitamin D core response.  
PC3 and U2OS show moderate slopes (~0.29–0.30), consistent with weaker but still positive trends.  
HA1E displays only a minor slope (~0.13), suggesting little or no consistent dose dependence in this context.  
Overall, effect sizes align with previous analyses (Spearman and HC3 regression), reinforcing the robustness of dose–response induction across most cell lines.

## 5.4 Bootstrap CIs for OLS slopes

**Goal.** Quantify the uncertainty of quick OLS slope estimates (`core_score ~ log10 dose`) using nonparametric bootstrap confidence intervals.  
This provides robust effect-size intervals that do not rely on parametric assumptions, complementing the HC3 regression (Section 4.3).

### Interpretation — Bootstrap CIs for slopes

- MCF7 and A549 show the strongest dose–response effects, with slopes ~0.45–0.50 and CIs well above zero.  
- PC3 and U2OS also display positive slopes, though with wider intervals, indicating moderate but consistent trends.  
- HA1E’s slope is small (~0.13) with a CI overlapping zero, suggesting no reliable dose dependence in this context.  
> Together, the bootstrap intervals reinforce robust dose–dependent activation of the Vitamin D core signature in most cell lines, especially in MCF7 and A549.

## 6.1 Preranked gene lists for enrichment

**Goal.** Translate dose–response results into **preranked gene lists** suitable for GSEA and Enrichr.  
We rank genes by their association with the Vitamin D core response, using consensus core scoring and per-cell effects.  
This step prepares standardized inputs for enrichment pipelines, ensuring comparability across cell lines and conditions.

## 6.2 GSEA (resumable, per cell line)

**Goal.** Test pathway-level enrichment using preranked gene lists for each cell line.  
We use a resumable, permutation-based procedure with checkpoints (per library × group), so long runs can be paused and resumed.

### Interpretation — GSEA (Hallmark & Reactome)

In A549, positive enrichment scores (ES > 0) with low FDR highlight pathway activation aligned with the Vitamin D–induced direction:

- **Hallmark:** strong enrichment of **E2F targets**, **Unfolded Protein Response**, **G2M checkpoint**, **mTORC1 signaling**, and **MYC targets**, indicating proliferative/cell-cycle programs and proteostasis/translation stress consistent with a stimulated transcriptional state.
- **Reactome:** enrichment for **DNA repair/replication** modules (e.g., meiotic/homologous recombination), **chromatin remodeling** (PBAF/BAF), **metabolic rewiring** (gluconeogenesis), and **histone arginine methylation**, supporting coordinated regulation of cell-cycle and epigenetic machinery.

The **leading-edge fraction** (~0.30–0.52) suggests a substantial subset of each gene set drives the signal. Cross-cell consistency (next figure) will distinguish shared vs. context-specific programs.

---

## 6.3 Dot-plot of top enriched pathways

**Goal.** Summarize the most enriched pathways across cell lines for each library.  
The dot size encodes gene set size; color encodes −log10(FDR). Groups on the x-axis are cell lines.

### Consensus pathway enrichment across cell lines

Across the Hallmark collection, **10 pathways were significantly enriched (FDR < 0.05) in at least 4 out of 5 cell lines**, indicating a high degree of cross-cell reproducibility. Among them, *UV response (early and late)*, *KRAS signaling*, *glycolysis*, *xenobiotic metabolism*, *adipogenesis*, and *mitotic spindle* reached significance in all five models, with positive enrichment scores (mean ES > 0.23) suggesting consistent activation. Stress-adaptive programs such as the *unfolded protein response* and *hypoxia* were detected in four cell lines, together with proliferative and inflammatory axes including *mTORC1 signaling*, *G2M checkpoint*, and *inflammatory response*.  

This consensus pattern points to a **core set of metabolic, proliferative, and stress-related pathways** modulated by vitamin D analogs, beyond context-specific transcriptional effects. The broad recurrence across diverse cellular backgrounds supports the existence of a conserved vitamin D transcriptional program that could represent common mechanistic drivers of its biological activity.

---

## 7. Visualization of directed results

To facilitate interpretation and ensure reproducibility, we assembled a set of publication-ready figures that summarize the main analyses. These include:  
(i) **forest plots** for dose–response slopes (OLS-HC3 estimates with confidence intervals),  
(ii) **box/strip plots** to visualize core scores across doses and cell lines, and  
(iii) **dot plots** highlighting the top enriched pathways by group.  

Together, these figures provide complementary perspectives on the transcriptional response to vitamin D analogs, enabling both quantitative comparison and biological interpretation.

### Dose–response slopes (HC3 regression)

Across cell lines, OLS–HC3 regression of *core_score ~ log10(dose)* revealed consistently positive slopes, indicating a monotonic activation of the Vitamin D core signature:

- **MCF7** showed the steepest slope (~0.55) with a narrow confidence interval and extremely significant *p*-value (*p* < 1e-8).  
- **A549** and **PC3** exhibited robust positive slopes (~0.40–0.45), also highly significant (*p* < 1e-5).  
- **U2OS** displayed a moderate slope (~0.28), significant but with wider uncertainty (*p* ≈ 0.043).  
- **HA1E** showed only a small, non-significant slope (~0.13; CI overlapping zero, *p* ≈ 0.15).

Together, these results indicate that four out of five tested cell lines display a statistically reliable dose–dependent increase in the Vitamin D core response, with effect sizes varying by cellular context.

###  7.2 Box + strip plots — core scores by dose and cell line

To visualize the distribution of Vitamin D core responses by dose and context, 
we plotted core scores stratified by **low vs high dose** within each cell line.  
Boxplots summarize the central tendency and variability, while overlaid strip 
points show individual signatures. This representation highlights both 
systematic trends and intra-group variability.


#### Interpretation - Core scores across doses and cell lines

Box/strip plots showed that core scores were consistently higher at **high dose** 
compared to **low dose** across most cell lines:

- **MCF7, A549, and PC3**: marked upward shift in distributions at high dose, 
  consistent with the strong positive slopes observed in regression analyses.  
- **U2OS**: modest increase in median core score, with broader within-group variability.  
- **HA1E**: overlapping distributions between low and high dose, with only a minor shift.

These visualizations confirm that the **dose-dependent induction** of the Vitamin D core 
signature is evident at the distribution level, particularly in MCF7, A549, and PC3.

### 7.3 Dot plots — top enriched pathways

To summarize the enrichment analyses, we generated dot plots of the **top pathways** 
from Hallmark and Reactome collections. In these plots, dot size reflects the gene set size, 
and color encodes −log10(FDR). The x-axis shows cell lines, and the y-axis lists 
the most significantly enriched pathways.

This visualization highlights both **shared programs** (pathways enriched in multiple 
cell lines) and **context-specific signals**.

### Enriched pathways across cell lines

Dot plots of top enriched pathways from **Hallmarks** and **Reactome** collections 
highlight both shared and context-specific programs.

- **Hallmarks**: Multiple cell-cycle and metabolic programs were consistently 
  enriched across lines, including *E2F targets*, *G2M checkpoint*, *mTORC1 signaling*, 
  *MYC targets*, and *glycolysis*. Stress-adaptive modules (*unfolded protein response*, 
  *hypoxia*) and signaling axes (*KRAS*, *TNFα/NFκB*, *estrogen response*) were also 
  recurrent. These results suggest a broad activation of proliferative, metabolic, 
  and stress-related pathways under vitamin D analog treatment.  

- **Reactome**: Enrichment was more heterogeneous, with strong signals in DNA repair 
  (*meiotic recombination*, *homologous recombination*, *ATR/replication stress*), 
  chromatin remodeling (*Polycomb/PBAF complexes*), and metabolic rewiring (*gluconeogenesis*). 
  In addition, signaling pathways (e.g., *Ephrin*, *ERBB2*, *Ras/FGFR*) and immune-related 
  modules (*NFE2L2 antioxidant response*, *IL-10 signaling*) emerged in specific contexts.  

Together, these pathway-level results indicate that vitamin D analogs elicit both 
**conserved transcriptional programs** (cell-cycle, metabolism, stress adaptation) 
and **context-dependent responses** (DNA repair, chromatin, immune signaling), 
reflecting the diversity of cellular backgrounds.
