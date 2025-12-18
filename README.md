# Vitamin D Transcriptomic Profiling (LINCS L1000)

This project presents a **reproducible and well-structured data science pipeline** for analyzing transcriptomic responses to **Vitamin D and its analogs** using the **LINCS L1000 (CMap 2020)** dataset.

The focus of the project is not biological discovery *per se*, but to demonstrate the ability to **handle complex biological datasets**, design **robust data pipelines**, perform **exploratory and directed analyses**, and extract **clear, defensible insights** from high-dimensional gene expression data.

---

## 🎯 Project Goals

- Build an end-to-end workflow for transcriptomic data analysis.
- Integrate raw public data into a structured relational database.
- Perform quality control and exploratory analysis on high-dimensional data.
- Assess consistency and context-dependence of compound-induced signatures.
- Communicate results clearly through clean visualizations and documentation.

---

## 📂 Repository Structure

```yalm 
vitD-transcriptomic-profiling/
│
├── backend/ # Django app: database models and populate/export commands
├── data/ # Curated datasets used in analysis
├── docs/ # Technical documentation and design notes
├── images/ # Diagrams and static assets
├── libs/ # Gene sets and auxiliary resources
├── notebooks/ # Jupyter notebooks (EDA and directed analyses)
├── results/ # Figures generated during analysis
├── src/vitd_utils/ # Utility library (stats, plotting, enrichment helpers)
├── requirements.txt
└── README.md
```

---

## 🔄 Workflow Summary

1. **Data Acquisition**  
   Public LINCS L1000 metadata and expression matrices were downloaded from [CLUE.io](https://clue.io/data/CMap2020#LINCS2020)

2. **Database Integration**  
   A Django + SQLite backend was implemented to organize compounds, cell lines, signatures, and expression data, enabling reproducible access and filtering.

3. **Data Subsetting**  
   The analysis focuses on Vitamin D and related analogs, with:
   - Fixed perturbation time (24 h)
   - Five human cell lines: `PC3`, `MCF7`, `A549`, `U2OS`, `HA1E`

4. **Exploratory Data Analysis (EDA)**  
   - Quality control using LINCS metrics (TAS, ss_ngene, cc_q75)
   - Dimensionality reduction (PCA, UMAP)
   - Hierarchical clustering and variance analysis
   - Assessment of replicate consistency

5. **Directed Analysis**  
   Targeted analyses were used to summarize transcriptional patterns and assess:
   - Consistency across compounds
   - Cell line–specific responses
   - Signal robustness across doses

6. **Visualization & Results**  
   Results are presented through clear, reproducible figures generated with modular plotting utilities.

---

## 📊 Key Analytical Insights

- Transcriptional signatures cluster more strongly by **cell line** than by compound, highlighting the importance of cellular context.
- Vitamin D analogs induce **consistent but heterogeneous** transcriptional responses across different cell types.
- A subset of compounds shows robust, reproducible signal across multiple quality metrics.
- Simple summary metrics can effectively capture overall transcriptional activity.

---

## ▶️ How to Run

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up the database:
```bash
cd backend
python manage.py migrate
python manage.py populate_compounds
python manage.py populate_signatures
```

Explore the analysis:
``` bash
jupyter lab notebooks/
```

## 📚 Additional Documentation

Detailed technical notes, database design decisions, and extended analysis commentary are available in the docs/ directory.

## 📌 Project Status
✅ Database backend implemented
✅ Data curated and subset defined
✅ Exploratory analysis completed
🚧 Directed analyses and visual refinements ongoing

---

📄 License & Data Source

This project is released under the MIT License.
Data are derived from the LINCS L1000 / CMap 2020 dataset provided by CLUE.io.

---
