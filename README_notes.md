### 📝 Notes for README – Cell Line-Specific Response

- PCA revealed that transcriptional signatures clustered **more clearly by cell line** than by compound.
- Signatures from **PC3 cells** showed a distinct transcriptional profile, separated from MCF7, U2OS, A549, and HA1E.
- This suggests that:
  - The response to vitamin D analogs is **cell-context dependent**.
  - PC3 may regulate a **different subset of genes** or show altered pathway activation compared to the other lines.
- These differences could reflect:
  - Variations in vitamin D receptor (VDR) expression,
  - Basal transcriptional states of the cells,
  - Or compound-cell line interactions affecting downstream signaling.

> 👉 Will highlight this as a key biological observation in the README summary and discussion.


## 📊 Exploratory Data Analysis (EDA): Vitamin D Transcriptomic Profiles

This exploratory analysis characterizes the transcriptional responses of human cell lines to Vitamin D and its analogs, using data from the LINCS L1000 dataset (CMap LINCS2020). The aim was to assess data quality, coverage, and compound-specific effects prior to downstream modeling or biological interpretation.

---

### 🔍 Key EDA Steps

- **Data Subsetting and Quality Control**  
  A curated subset of the LINCS L1000 data was used, focused exclusively on compound perturbations related to Vitamin D (e.g., calcitriol, calcipotriol, maxacalcitol).  
  High-quality transcriptional signatures were selected using metadata filters:
  - *TAS ≥ 0.2* (Transcriptional Activity Score)
  - *CC_Q75 ≥ 0.2* (75th percentile of connectivity correlation)
  - *ss_ngene ≥ 40* (number of significantly modulated genes)

- **Exploratory Visualizations**  
  Several projection and clustering techniques were used to visualize global structure:
  - **PCA** and **UMAP** revealed partially overlapping gene expression profiles across compounds.
  - A **hierarchical clustering heatmap** of top-modulated signatures highlighted the heterogeneity and compound-specific effects in gene regulation.

- **Gene Modulation Analysis**  
  - The **top 20 most modulated genes** were identified based on the mean absolute z-score across all signatures.
  - A barplot summarized the strongest targets of Vitamin D transcriptional influence, including *IGFBP3*, *DDIT4*, and *TSKU*.

- **Compound Similarity and Correlation**  
  - Correlation heatmaps were generated to compare compounds based on their average modulation profiles across the top genes.
  - These analyses revealed distinct co-regulation patterns, supporting the hypothesis that different analogs—while mechanistically related—induce specific expression fingerprints.

---

### 📌 Summary of Insights

- Vitamin D analogs elicit diverse transcriptional responses, both in magnitude and gene-specific modulation.
- High-quality signatures are unevenly distributed across compounds, with some analogs showing consistently strong effects (TAS > 0.3).
- Gene co-modulation patterns suggest potential for compound clustering, mechanistic inference, and downstream predictive modeling.

---

> All results in this section were derived from the Level 5 z-score matrix (`level5_beta_trt_cp_n720216x12328.gctx`) and relevant metadata downloaded from [CLUE.io](https://clue.io/data/CMap2020). For full reproducibility, see data processing scripts in the `notebooks/eda/` folder.
