# EDA 01 – Dataset Filtering and Subset Definition

## Purpose

The goal of this step was to define a **clean, consistent, and biologically
meaningful subset** of the LINCS L1000 dataset focused on Vitamin D and related
analogs, suitable for downstream exploratory and comparative analyses.

Given the heterogeneity of LINCS experiments, this step prioritizes:
- data coverage
- experimental consistency
- interpretability over maximal size

---

## Data Sources

The following LINCS metadata files were used:

- `compoundinfo_beta.txt` – compound identifiers and annotations
- `instinfo_beta.txt` – experimental conditions (dose, time, cell line)
- `siginfo_beta.txt` – transcriptomic signature metadata
- `level5_beta_trt_cp_n720216x12328` – Level 5 z-score matrix (`.gctx`)

---

## Identification of Vitamin D–Related Compounds

A broad keyword-based search was performed across all compound metadata fields to capture Vitamin D and closely related analogs (e.g. *calcitriol*, *calcipotriol*, *paricalcitol*).

After extracting the corresponding `pert_id` values, we filtered the experimental conditions (`instinfo_beta.txt`) and summarize:

- The most frequent compounds
- The most represented cell lines
- The most common exposure times

This sets the foundation for selecting a biologically meaningful and well-supported subset for transcriptomic analysis.

This inclusive strategy was chosen to avoid missing relevant perturbagens due to naming or annotation variability.

From the full dataset, **5,919 experimental conditions** involving Vitamin D–related compounds were identified.

---

## Exploratory Summary of Experimental Coverage

The filtered experimental conditions were summarized to assess coverage across:

- **Compounds**
- **Cell lines**
- **Exposure times**

Key observations:

- Seven compounds dominate the dataset:
  *Calcitriol, Calcipotriol, Maxacalcitol, Seocalcitol, Ercalcitriol,
  Tacalcitol, Paricalcitol*.
- **24-hour exposure** is by far the most frequent condition
  (≈ 74% of experiments).
- Five cell lines show robust representation:
  `MCF7`, `A549`, `PC3`, `HA1E`, `U2OS`.

This combination provides a balance between biological diversity and statistical
robustness.

---

## Subset Design Decisions

Based on coverage and consistency, the final subset was defined as:

- **7 compounds**
- **5 cell lines**
- **24 h exposure time**

Coverage across compound–cell line combinations was inspected prior to final
selection.

Two combinations were missing:
- Maxacalcitol – U2OS
- Paricalcitol – U2OS

These gaps were considered acceptable, as:
- U2OS is well represented for other compounds
- Slight imbalance is expected in real-world high-throughput datasets
- Removing U2OS would reduce biological diversity without improving coverage
substantially

Final design:
**7 compounds × 5 cell lines × 24 h (minus 2 missing combinations)**

---

## Quality Control Criteria
- To ensure data quality, we filtered the 422 matched signatures to retain only those with **at least 3 biological replicates** (`nsample ≥ 3`).

---

## Outcome

- **258 high-quality transcriptomic signatures** selected
- Expression matrix extracted from Level 5 data
- Dataset saved for downstream EDA and directed analyses

This filtered subset serves as the foundation for all subsequent analyses in
the project.
