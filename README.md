# Vitamin D Transcriptomic Profiling (LINCS L1000)

This repository hosts a **reproducible data-science workflow** to analyze transcriptomic responses to **Vitamin D and its analogs** using the **LINCS L1000** dataset (Connectivity Map / CMap project).  
The goal is to identify **core gene signatures, dose–response patterns, and pathway enrichments** across multiple human cell lines, using an integrated pipeline of **data engineering, statistical analysis, and visualization**.

---

## 📂 Repository Structure

```
vitD-transcriptomic-profiling/
│
├── raw_data/         # Manually downloaded LINCS files (metadata + GCTX subset)
├── backend/          # Django app: database models + populate/export commands
├── exports/          # Curated project subsets (CSV/Parquet, aligned with DB)
├── notebooks/        # Jupyter notebooks (EDA, directed analyses, results)
├── src/vitd_utils/   # Utility library (config, gsea, stats, plotting, etc.)
├── results/          # Figures and tables for publication
└── README.md         # Project overview
```

---

## 🔄 Workflow Overview

1. **Raw Data Acquisition**  
   - Download LINCS2020 metadata and compound expression matrix from [CLUE.io](https://clue.io/data/CMap2020#LINCS2020).  
   - Keep original filenames (no renaming required).

2. **Database Integration (Django backend)**  
   - Models: `Compound`, `CellLine`, `Signature`, `Gene`, `ExpressionMatrixEntry`.  
   - Populate scripts load raw files into a relational SQLite DB.  
   - Subsets are exported via management commands.

3. **Subset Definition**  
   - Vitamin D and analogs only.  
   - Perturbation time fixed at **24 h**.  
   - Five cell lines: `PC3`, `MCF7`, `A549`, `U2OS`, `HA1E`.  
   - Exported as aligned metadata + expression matrices (CSV/Parquet).

4. **Exploratory Data Analysis (EDA)**  
   - Quality control metrics (TAS, ss_ngene, cc_q75).  
   - PCA, UMAP, and hierarchical clustering.  
   - PERMANOVA: variance explained by cell line, compound, and dose.  
   - Visualization of expression distributions and replicate consistency.

5. **Directed Analyses**  
   - **Core VDR signature**: intersection of consistently regulated genes.  
   - **Dose–response**: monotonicity tests (Spearman ρ), OLS slopes.  
   - **Pathway enrichment**: GSEA/Enrichr on per-cell UP/DOWN lists.  
   - **Core score**: single metric summarizing VDR activity.

6. **Results & Figures**  
   - Forest plots, box/strip plots, dot plots (publication-ready).  
   - Organized in `results/figures`.  
   - Code modularized in `src/vitd_utils/plotting.py`.

---

## ⚙️ Requirements

- Python >= 3.11  
- Recommended: `conda` or `venv`

Main libraries:
```
pandas, numpy, matplotlib, seaborn,
scikit-learn, statsmodels, gseapy,
django, pyarrow
```

---

## ▶️ Usage

Clone repository and install dependencies:
```bash
git clone https://github.com/paulairazoqui/vitD-transcriptomic-profiling.git
cd vitD-transcriptomic-profiling
pip install -r requirements.txt
```

Set up database:
```bash
cd backend
python manage.py migrate
python manage.py populate_compounds
python manage.py populate_signatures
python manage.py export_subset --outdir "../exports"
```

Explore analysis:
```bash
jupyter lab notebooks/
```

---

## 📌 Project Status

- ✅ Database implemented and populated.  
- ✅ Subset exported and curated.  
- ✅ EDA completed.  
- ✅ Utility library (`vitd_utils`) created.  
- 🚧 Directed analyses and figures in progress.  
- 🔜 Folder-level READMEs and full documentation.

---

## 📄 License

This project is released under the MIT License.  
Data comes from the **CLUE LINCS2020 dataset** ([CMap Project](https://clue.io/data/CMap2020#LINCS2020)).












































































































# 🧬 Vitamin D Transcriptomic Profiling using LINCS L1000 Data

This project investigates the transcriptional response of human cell lines to Vitamin D and its analogs, using publicly available gene expression profiles from the LINCS L1000 dataset (GSE70138).

The workflow integrates raw L1000 data into a structured relational database (Django + SQLite) to enable reproducible data access and linkage between compounds, cell lines, molecular signatures, and expression matrices.

The objectives are to:

- Characterize the molecular signatures induced by Vitamin D compounds across multiple human cell lines.
- Identify potential gene expression biomarkers of Vitamin D response.
- Develop predictive machine learning models to classify or quantify compound effects based on transcriptomic data.

This work combines transparent data processing, rigorous exploratory data analysis (EDA), and predictive modeling, with the aim of generating biologically meaningful insights and serving as the foundation for a scientific preprint or publication.


---

## 🔁 Quick start (reproducibility)

To reproduce the environment:

```bash
# 1. Clone the repository
git clone https://github.com/paulairazoqui/vitD-transcriptomic-profiling.git
cd vitD-transcriptomic-profiling

# 2. Create and activate the virtual environment
python -m venv vitd_env
# On Windows (PowerShell)
.\vitd_env\Scripts\activate
# On Linux/Mac
source vitd_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

> 💡 For detailed setup instructions, including OS-specific notes and troubleshooting, see  
> [docs/environment_setup.md](docs/environment_setup.md).

---


