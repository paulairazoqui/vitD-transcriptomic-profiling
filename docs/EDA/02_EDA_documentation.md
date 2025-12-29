# Exploratory Data Analysis of Vitamin D-Related Transcriptional Signatures

This notebook presents the exploratory data analysis (EDA) of transcriptional responses to vitamin D and its analogs, based on data from the LINCS L1000 dataset. The dataset includes gene expression signatures from human cell lines exposed to different vitamin D-related compounds across various doses and time points.

The goal of this analysis is to characterize the diversity and distribution of the selected signatures, examine the experimental conditions (cell lines, doses, exposure times), and identify preliminary patterns in gene expression profiles that may inform subsequent modeling and biological interpretation.

## Overview of Vitamin D Signature Annotations

🧠 General structure and data types
📏 Summary statistics for numeric columns
🔣 Cardinality of categorical variables
⚠️ Missing value check

This section summarizes the characteristics of the filtered metadata, which includes only signatures related to vitamin D analogs. The dataset was preselected to include:

- **7 compounds** of interest
- **5 human cell lines**
- A single exposure time of **24 hours**

As expected, all signatures reflect this uniformity in treatment duration and compound class. The resulting dataset contains **258 transcriptional signatures**, each associated with a set of experimental and quality control annotations (37 columns in total).

#### 🧪 Quality control and metadata insights

- All signatures have valid values for key fields such as `dose`, `cell line`, and `perturbation type`.
- The `Transcriptional Activity Score (tas)` ranges from 0.01 to 0.64, indicating heterogeneity in transcriptional response even among filtered compounds.
- `ss_ngene` (number of genes significantly changed) varies widely, from 43 to 646.
- The `batch_effect_tstat` and reproducibility scores (`median_recall_*`) show moderate variability, suggesting batch or replicate-level effects worth considering in downstream analysis.

#### ⚠️ Missing values

Most columns are complete. Only `build_name` is entirely missing, and some metrics related to recall and connectivity have partial missingness, which will be handled accordingly if required.

> This metadata summary confirms that the pre-filtering step was correctly applied and that the dataset retains sufficient variability in response quality and intensity to support further exploration.

This section explores the structure and distribution of the gene expression matrix (`exp_df`) corresponding to the filtered vitamin D-related transcriptional signatures.

### 📐 Matrix dimensions

The expression matrix contains:
- **12,328 genes** (rows)
- **258 signatures** (columns), each matching an experimental condition from the metadata.

Each value represents a **z-score normalized gene expression level**, as provided by the LINCS L1000 pipeline.

### 📊 Summary statistics

A preview of the data shows expected values centered around zero, with both up- and down-regulated genes across conditions. Descriptive statistics confirm this distribution:

- Expression values range from approximately **-8.48 to +9.56**.
- Signature-wise and gene-wise variances are both moderate on average (mean ~0.42).
- **No genes** were found with near-zero variance, indicating that all genes carry some signal and no immediate filtering is needed.

### 📈 Distribution of expression values

The histogram below shows a bell-shaped distribution, consistent with the z-score normalization applied to the data. The central peak is located at 0, and the tails extend in both directions, confirming the presence of genes with both induced and repressed expression across conditions.

>This analysis confirms that the expression matrix is well-structured, contains biologically meaningful variation, and is ready for dimensionality reduction or clustering in subsequent steps.

📌 Signature distribution across key experimental factors

## PCA of Gene Expression Signatures

Principal Component Analysis (PCA) was applied to the gene expression matrix to visualize the structure of the 258 vitamin D-related transcriptional signatures.

This dimensionality reduction technique allows us to:
- Identify potential clustering of signatures by compound or cell line,
- Detect outliers or batch effects,
- Understand how much variance is captured in low-dimensional projections.

The PCA was performed on the **z-score normalized expression matrix** (`exp_df`), already aligned with the metadata.

#### Interpretation of PCA Results

The PCA projection of the 258 vitamin D-related transcriptional signatures reveals the following:

- **No strong global separation** between compounds is observed, indicating that the overall gene expression profiles are partially overlapping across vitamin D analogs.
- Some mild clustering tendencies appear for specific compounds, such as *maxacalcitol* and *paricalcitol*, which show a few more dispersed or distinctive points—suggesting **unique transcriptomic effects** under certain conditions.
- The explained variance is relatively low (PCA1: 13.6%, PCA2: 5.4%), consistent with high-dimensional biological data. This suggests that a **large number of components** may be needed to capture the full complexity of variation.

> These results suggest that while the compounds share global expression patterns—likely due to their common vitamin D activity—specific outliers may reflect differences in potency, cell type interaction, or downstream pathways activated.

### PCA Colored by Cell Line

To investigate whether cell type explains more variance than compound identity, we re-colored the PCA projection using the `cell_mfc_name` variable.
#### Interpretation: PCA Colored by Cell Line

When the same PCA projection is colored by cell line, a clearer structure emerges:

- **PC3 signatures** (orange) form a distinct cluster, mainly in the upper half of the plot, showing a consistent transcriptional pattern across compounds.
- **MCF7, A549, U2OS, and HA1E** signatures largely overlap, suggesting more similar expression responses or lower variability among them.
- This indicates that **cell type has a stronger effect** on the transcriptional landscape than compound identity alone, at least in the space captured by the first two principal components.

> These findings highlight the importance of cellular context in shaping the response to vitamin D analogs, and suggest that stratified analysis by cell line may be necessary in downstream modeling.

## Clustering of Expression Signatures – Heatmap with Dendrogram

To explore the relationships between transcriptional signatures, we used hierarchical clustering on the top 100 most variable genes across all conditions. This clustermap visualizes both sample-sample and gene-gene similarity.

Signatures are annotated by cell line, allowing us to assess whether they cluster according to biological condition.

### Interpretation – Clustermap of Top 100 Variable Genes

The hierarchical clustering of gene expression signatures reveals structured patterns of co-expression:

- Signatures from **PC3 cells** cluster tightly, reinforcing their distinct transcriptional response to vitamin D analogs.
- Other cell lines (MCF7, A549, HA1E, U2OS) show more **distributed clustering**, suggesting overlapping but not identical responses.
- Specific gene clusters display coordinated upregulation or downregulation across subsets of conditions, potentially reflecting shared pathways or regulatory modules.

> These results validate and extend the PCA observations, showing that cell line identity remains a strong driver of expression variability, even at the level of the most variable genes.

## UMAP of Gene Expression Signatures

To complement the PCA and clustering analysis, we applied **Uniform Manifold Approximation and Projection (UMAP)** to the expression matrix. UMAP is a non-linear dimensionality reduction technique that preserves both local and global structure in the data.

This method is particularly useful for detecting subtle patterns and **natural groupings** that may not be captured by PCA. Here, we visualize the transcriptional signatures in a 2D space using UMAP, colored by **cell line identity**.
#### Interpretation of UMAP Results

The UMAP projection of gene expression signatures across selected cell lines reveals the following:

- **Clear separation** is observed for the PC3 cell line, which forms a distinct and compact cluster—suggesting a **consistent and unique transcriptomic response** compared to the other lines.
- **Partial overlap** is present among MCF7, A549, HA1E, and U2OS, indicating **shared or more variable expression profiles**, possibly due to common pathways or cell-type similarities.
- UMAP maintains meaningful **local structure** in the data, capturing both discrete and continuous relationships between samples.
- Unlike PCA, UMAP is non-linear and does not provide explained variance metrics, but its **visual separability** implies underlying biological differences.

> These observations highlight how transcriptional responses to perturbagens can vary by cell type. While some cell lines (e.g., PC3) respond in a well-defined manner, others exhibit broader variability, potentially reflecting differences in lineage, basal gene expression, or compound sensitivity.

## Distribution of Experimental Metrics by Compound and Cell Line

To evaluate the consistency and variability of transcriptional responses, we visualize three key metrics from the metadata:

- `tas`: Transcriptional Activity Score
- `ss_ngene`: Number of significantly changed genes
- `cc_q75`: 75th percentile of replicate correlation (quality control)

These metrics reflect signal strength, gene-level impact, and reproducibility, respectively. We compare their distributions across compounds (`cmap_name`) and cell lines (`cell_mfc_name`) to assess whether specific treatments or cellular contexts show stronger or more variable responses.


### 🔹 Distribution by Compound
#### 🧠 Interpretation – Metrics by Compound

The boxplots of `tas`, `ss_ngene`, and `cc_q75` across vitamin D-related compounds reveal moderate variability, with no single compound showing consistently superior performance across all metrics.

- **TAS** values are broadly comparable across compounds, suggesting similar overall transcriptional activity. Slightly higher medians are observed for *tacalcitol*, *seocalcitol*, and *paricalcitol*.
- **ss_ngene**, representing the number of significantly changed genes, shows the highest dispersion for *paricalcitol*, indicating strong but variable gene-level responses.
- **cc_q75**, a proxy for replicate consistency, is relatively balanced, though *maxacalcitol* and *paricalcitol* exhibit marginally higher median values.

> These results suggest that all compounds induce measurable transcriptional activity, but the **strength and reproducibility** of responses vary slightly across analogs.

### 🔹 Distribution by Cell Line
### 🧬 Cell Line Comparison of Transcriptomic Response Metrics

The distribution of transcriptional activity metrics across cell lines reveals that **cellular context strongly shapes the magnitude and reproducibility of responses to vitamin D analogs**.

- **PC3 cells** stand out with **higher median TAS**, **more significantly altered genes (ss_ngene)**, and **stronger replicate correlation (cc_q75)**, indicating a robust and consistent transcriptional signature.
- Nonetheless, **other cell lines such as MCF7, U2OS, A549, and HA1E also show meaningful transcriptomic changes**, with **median `ss_ngene` values often exceeding 100–150 genes**, a level considered biologically significant in many studies.
- **Higher variability** in `cc_q75` across some lines (e.g., A549, HA1E) might reflect lower reproducibility or more heterogeneous responses—important to keep in mind for downstream modeling or interpretation.

> These results support the notion that **vitamin D analogs produce broad transcriptional effects across multiple cancer-related cell types**, with **PC3 being particularly responsive**, but by no means the only relevant model.

### 📊 Distribution of Transcriptomic Signatures per Cell Line

Before diving deeper into transcriptional patterns, it's essential to assess the **representation of each cell line** in our dataset. A highly responsive cell line may appear to perform better simply due to a **larger number of replicates** or signatures. This plot helps evaluate whether the observed trends reflect biological differences or data imbalance.

#### 📌 Count the number of transcriptomic signatures available per cell line
The distribution of vitamin D-related transcriptomic signatures is relatively balanced across the main cell lines, with **MCF7, PC3, A549, and HA1E** each contributing over 50 signatures. **U2OS** has fewer profiles (~20), which may slightly limit statistical power for this cell type.

This coverage is consistent with the compound × cell line matrix, where *calcitriol* is the most widely tested analog across all lines. Other compounds like *tacalcitol* or *seocalcitol* show more limited sampling, but still span multiple cell types.

> Therefore, the observed transcriptional differences between cell lines are **not simply due to data imbalance**, and likely reflect genuine biological context effects.

### 🔬 Most Strongly Modulated Genes Across All Signatures

To identify the genes most responsive to vitamin D analogs, we computed the **mean absolute z-score** for each gene across all 258 transcriptional signatures.

This metric captures the overall magnitude of transcriptional change, regardless of direction (up- or down-regulation). Genes with higher mean |z| values are considered **globally more responsive** to vitamin D perturbation.

#### 📌 Identify the top 20 most strongly modulated genes across all signatures
#### 🧠 Interpretation – Top Modulated Genes

The analysis of mean absolute z-scores across all 258 vitamin D-related transcriptional signatures highlights several genes with consistently strong modulation:

- **IGFBP3** and **DDIT4** top the list, both of which are known to be regulated by vitamin D and associated with apoptosis, cellular stress, and proliferation control.
- Other highly responsive genes include **TXNRD1** (oxidative stress), **NFKBIA** (inflammation), **PHGDH** (serine biosynthesis), and **SPP1** (osteopontin), all of which play roles in cellular homeostasis and cancer biology.
- The presence of **C2CD2**, **TSKU**, and other less characterized genes suggests possible **novel regulatory effects** of vitamin D analogs worthy of further investigation.

> These findings support the hypothesis that vitamin D analogs elicit biologically relevant transcriptional responses, impacting both well-known and potentially novel gene targets.

### 🔥 Heatmap of Top 20 Most Modulated Genes

To explore how the most responsive genes behave across all transcriptional signatures, we created a heatmap of z-score expression values for the **top 20 most modulated genes**. This visualization reveals potential clustering patterns among compounds, cell lines, and gene regulation modes.

### 🧬 Interpretation – Heatmap of Top 20 Most Modulated Genes

The heatmap reveals **coherent transcriptional response patterns** among the top 20 most modulated genes across vitamin D-related signatures.

- Distinct clusters of gene activation (red) and repression (blue) are visible, indicating **co-regulation** and potential **shared pathways**.
- Several genes, such as **IGFBP3**, **DDIT4**, and **TXNRD1**, show strong and consistent upregulation in subsets of signatures.
- Column annotations by cell line confirm that some cell types (e.g., **PC3**) exhibit **stronger and more consistent responses**, aligning with previous PCA and metric-based observations.

> These expression profiles suggest that both compound and cellular context shape the transcriptional landscape, and that a subset of genes may serve as robust indicators of vitamin D activity.

### 🧪 Activity Intensity by Compound and Cell Line

To summarize the strength of transcriptional responses across experimental conditions, we computed the average **Transcriptional Activity Score (TAS)** for each combination of **compound** and **cell line**.

This heatmap highlights which cell-compound contexts exhibit the strongest overall modulation, guiding future analyses or experimental prioritization.

#### 🧬 Observations on Transcriptional Activity Score (TAS)

- The **PC3** cell line shows the **highest transcriptional response** across all Vitamin D analogs, with TAS values consistently above 0.30. This suggests that prostate cancer cells may be particularly sensitive to modulation by these compounds.

- **Ergocalcitriol, paricalcitol, and seocalcitol** appear to induce **stronger transcriptional activity overall**, especially in PC3, pointing to potential differences in potency or mechanism compared to calcitriol.

- In contrast, **U2OS (osteosarcoma)** and **A549 (lung cancer)** lines show **weaker transcriptional responses**, with TAS values typically below 0.20, indicating limited gene expression modulation under the tested conditions.

- **MCF7** (breast cancer) and **HA1E** (kidney epithelial) display **moderate and variable TAS values**, suggesting context-dependent sensitivity that may reflect differences in Vitamin D receptor expression or downstream signaling.

> These patterns highlight the importance of cell-type specificity when evaluating the transcriptomic impact of Vitamin D analogs and may inform future therapeutic targeting strategies.

### 🧠 Comparison of Correlation Analyses: Treatment Similarity vs. Gene Co-regulation

To gain a more complete understanding of the transcriptional effects of vitamin D analogs, we performed **two complementary correlation analyses** on the expression matrix.

#### 🔵 1. Gene Co-regulation Across Vitamin D Treatments

**Analysis:**  
We computed the **Pearson correlation between genes** (rows of the expression matrix), across all vitamin D signatures.

**Question addressed:**  
*Which genes tend to behave similarly in response to vitamin D analogs?*

**Biological interpretation:**
- Co-regulated genes may share **regulatory elements**, belong to the same **pathways**, or be **core effectors** of the vitamin D response.
- Highly correlated genes might be **redundant**, while inversely correlated ones may represent **divergent pathways**.
- This helps identify **candidate biomarkers** or **functional modules** activated by treatment.

#### *🔬 Key Insights from Gene Co-regulation Heatmap*

This heatmap reveals patterns of **co-regulation among the top 20 genes** most modulated by vitamin D analogs.  
Notably:

- Several gene pairs show **strong positive correlation** (e.g., `MMP1` and `NPC1`), suggesting shared regulatory mechanisms or involvement in similar pathways.
- A few genes, such as `MTHFD2` and `PRSS23`, exhibit **anti-correlated patterns**, potentially reflecting opposing functional roles.
- These insights can help prioritize **candidate genes for downstream pathway analysis or biomarker development**.

### 🔴 2. Treatment Similarity Based on Gene Expression Profiles

**Analysis:**  
We computed the **Pearson correlation between treatment signatures** (columns of the expression matrix), using the top 20 most modulated genes.

**Question addressed:**  
*How similar are the transcriptomic responses induced by different vitamin D analogs?*

**Biological interpretation:**
- Compounds that cluster together in this analysis likely activate **similar transcriptional programs**.
- Differences may reflect **distinct receptor affinity**, **cellular uptake**, or **mechanistic selectivity**.
- This is useful to identify **functionally similar compounds**, even when their chemical structure differs — a principle applied in **drug repurposing**.

#### *🧬 Gene-Gene Correlation Across All Vitamin D Signatures*

This plot shows the **pairwise Pearson correlation** between the top 20 modulated genes across all vitamin D-related signatures (i.e., individual experimental conditions).

- Genes such as `TXNRD1`, `C2CD2`, and `NFKBIA` show **consistent co-modulation patterns**, suggesting robust responses across conditions.
- Strong negative correlations (e.g., between `PRSS23` and `TXNRD1`) may indicate **functionally opposing transcriptional programs**.
- These patterns reflect the **global coordination or antagonism** of gene responses to vitamin D analog exposure, independent of specific compounds.

> This heatmap helps assess how **stable or divergent gene relationships** are across the entire dataset, which can be crucial for identifying network modules or regulatory axes.

### ✅ Why both analyses are important

| Analysis                                | Focus                       | Key Insight                        |
|----------------------------------------|-----------------------------|------------------------------------|
| **Treatment Similarity** (`df.corr()`) | Across treatments           | Groups compounds by response       |
| **Gene Co-regulation** (`df.T.corr()`) | Across genes                | Reveals functional gene modules    |

By running both, we explore **how compounds behave**, and **what genes co-operate**, providing a more holistic view of the transcriptional landscape.
