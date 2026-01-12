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


### Linking `Instance` to `Signature`

In the original LINCS L1000 data, the file `instinfo_beta.txt` contains detailed metadata for each experimental instance (e.g., plate ID, well ID, QC metrics), but it **does not include the `sig_id`** needed to establish the foreign key relationship with the `Signature` table.

Instead, the `sig_id` can be found in `siginfo_beta.txt`, specifically in the `distil_ids` column. This column stores a list of `instance_id` values (`sample_id` in `instinfo_beta.txt`) that belong to each signature.

To correctly populate the `Instance` model, the following steps are required:

1. **Load** `instinfo_beta.txt` to extract all instance-level data.
2. **Load** `siginfo_beta.txt` and build a mapping from each `instance_id` to its corresponding `sig_id` via the `distil_ids` field.
3. **Insert** records into the `Instance` table, assigning the appropriate `Signature` foreign key for each instance.

This two-file approach ensures relational integrity in the database and preserves the correct mapping between raw LINCS instances and their associated signatures.

---

### Instances without `sig_id` match

During the population of the `Instance` table, some rows from `instinfo_beta.txt` may not find a matching `sig_id` in `siginfo_beta.txt`. This is expected behavior and not an error.

**Why it happens:**
- The project may only load a filtered subset of signatures into the database (e.g., specific compounds, cell lines, or experimental conditions).
- `instinfo_beta.txt` contains instances from *all* LINCS experiments, including those not present in our `Signature` table.
- When an `instance_id` (`sample_id`) is not listed in any `distil_ids` from `siginfo_beta.txt` that we have loaded, it is skipped to preserve referential integrity.

**Impact:**
- Skipped instances are simply ignored; they do not appear in the database.
- The `no sig match` count in the logs is a diagnostic to show how many rows were skipped for this reason.

**Conclusion:**
This filtering is intentional. It ensures that every `Instance` stored in the database has a valid foreign key reference to an existing `Signature`.

---

VDR Expression in the Cell Lines (Based on Tissue Origin)


| Cell Line                 | Tissue of Origin | VDR Expression Insight                                                                                                                                |
| ------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A549** (lung carcinoma) | Lung             | *Low VDR expression reported* in A549 cells, especially with KRAS mutations ([PMC][1]).                                                               |
| **MCF7** (breast cancer)  | Breast           | *High endogenous VDR expression*, common target in knockdown studies ([PMC][2], [BioMed Central][3]).                                                 |
| **PC3** (prostate cancer) | Prostate         | No direct evidence from the hits, but prostate epithelium generally expresses VDR—common in hormone-responsive research (though unconfirmed for PC3). |
| **U2OS** (osteosarcoma)   | Bone             | No direct data found here. Given bone’s responsiveness to vitamin D, some basal VDR expression is plausible, but needs confirmation.                  |
| **HA1E** (renal origin)   | Kidney           | No direct citation for VDR in HA1E; kidney tissue typically expresses VDR, but specific data on this line wasn’t found.                               |

[1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC3396768/?utm_source=chatgpt.com "Characterization of vitamin D receptor (VDR) in lung ..."
[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC5432290/?utm_source=chatgpt.com "The vitamin D receptor is involved in the regulation ..."
[3]: https://bmcgenomics.biomedcentral.com/articles/10.1186/1471-2164-10-499?utm_source=chatgpt.com "Anti-proliferative action of vitamin D in MCF7 is still active after ..."
