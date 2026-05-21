**Operational Metadata**
- **Documented notebook path:** `docs/notebooks/01_filtering_documentation.md`
- **Five-track role:** Data curation and subset-definition track (Track 1 of 5)
- **Status:** Completed
- **Purpose:** Document filtering logic and rationale used to define the Vitamin D manuscript subset for downstream analyses.
- **Main inputs:** LINCS metadata tables (`compoundinfo_beta.txt`, `instinfo_beta.txt`, `siginfo_beta.txt`) and Level 5 matrix (`level5_beta_trt_cp_n720216x12328.gctx`).
- **Main outputs / artifacts:** Curated Vitamin D subset specification (7 compounds × 5 cell lines × 24 h), selected signature set, and documented filtering decisions for subsequent notebooks.

# EDA 01 — Dataset Filtering and Subset Definition

## Objective

The objective of this step is to define a **clean, consistent, and biologically meaningful subset** of the LINCS L1000 dataset focused on **Vitamin D and related analogs**, suitable for downstream exploratory, comparative, and modeling analyses.

Given the intrinsic heterogeneity of LINCS experiments, this stage prioritizes:

- experimental consistency  
- biological interpretability  
- sufficient data coverage  

over maximizing raw dataset size.

This filtering step establishes a robust foundation for all subsequent analyses in the project.

---

## Data Sources

The following LINCS metadata and expression files were used:

- `compoundinfo_beta.txt` — compound identifiers and annotations  
- `instinfo_beta.txt` — experimental conditions (dose, time, cell line)  
- `siginfo_beta.txt` — transcriptomic signature metadata  
- `level5_beta_trt_cp_n720216x12328.gctx` — Level 5 gene expression matrix (z-scores)

---

## Identification of Vitamin D–Related Compounds

To capture Vitamin D and closely related analogs, a **broad keyword-based search** was performed across all compound metadata fields. This approach aimed to minimize false negatives caused by naming variability or incomplete annotations.

Examples of captured compounds include:

- Calcitriol  
- Calcipotriol  
- Paricalcitol  
- Ercalcitriol  
- Tacalcitol  

All matching `pert_id` values were extracted and used to filter the experimental conditions in `instinfo_beta.txt`.

This inclusive strategy was intentionally chosen to preserve biological relevance while avoiding overly restrictive compound selection at this early stage.

From the full LINCS dataset, **5,919 experimental conditions** involving Vitamin D–related perturbagens were identified.

---

## Exploratory Assessment of Experimental Coverage

The filtered experimental conditions were summarized to evaluate coverage across key dimensions:

- **Compounds**
- **Cell lines**
- **Exposure times**

Key observations:

- Seven compounds dominate the dataset:  
  *Calcitriol, Calcipotriol, Maxacalcitol, Seocalcitol, Ercalcitriol, Tacalcitol, Paricalcitol*
- **24-hour exposure** represents approximately **74%** of all experiments.
- Five cell lines show strong and consistent representation:  
  `MCF7`, `A549`, `PC3`, `HA1E`, `U2OS`

This distribution provides a favorable balance between biological diversity and statistical robustness.

---

## Subset Design Rationale

Based on coverage, consistency, and interpretability, the final subset was defined using the following criteria:

- **7 compounds**
- **5 cell lines**
- **24-hour exposure time**

Coverage across compound–cell line combinations was explicitly inspected prior to final selection.

Two combinations were absent:

- Maxacalcitol – U2OS  
- Paricalcitol – U2OS  

These gaps were considered acceptable because:

- U2OS is well represented for other compounds  
- Minor imbalance is expected in high-throughput datasets  
- Removing U2OS would reduce biological diversity without substantially improving coverage

Final design:

**7 compounds × 5 cell lines × 24 h exposure (minus 2 missing combinations)**

---

## Quality Control Criteria

To ensure transcriptomic robustness, the matched signatures were filtered to retain only those with:

- **At least 3 biological replicates** (`nsample ≥ 3`)

After compound/cell-line/timepoint selection and this `nsample ≥ 3` criterion, **422 metadata-level candidate signatures** remained. A later expression-matrix completeness step removes signatures without usable expression values and realigns metadata to the expression matrix.

---

## Outcome

- **258 final analysis-ready, expression-complete manuscript signatures** selected
- Expression data extracted from Level 5 z-score matrix  
- Final dataset saved for downstream exploratory analysis and targeted modeling

This curated subset constitutes the reference dataset for all subsequent analyses in the project.
