# 🧬 Vitamin D Transcriptomic Profiling using LINCS L1000 Data

This project investigates the transcriptional response of human cell lines to Vitamin D and its analogs, using publicly available gene expression profiles from the LINCS L1000 dataset (GSE70138).

The workflow integrates raw L1000 data into a structured relational database (Django + SQLite) to enable reproducible data access and linkage between compounds, cell lines, molecular signatures, and expression matrices.

The objectives are to:

- Characterize the molecular signatures induced by Vitamin D compounds across multiple human cell lines.
- Identify potential gene expression biomarkers of Vitamin D response.
- Develop predictive machine learning models to classify or quantify compound effects based on transcriptomic data.

This work combines transparent data processing, rigorous exploratory data analysis (EDA), and predictive modeling, with the aim of generating biologically meaningful insights and serving as the foundation for a scientific preprint or publication.


---

## 🔁 Reproducibility: setting up the environment

This project uses a virtual environment to ensure reproducibility and avoid dependency issues.

### 1. Clone the repository

```bash
git clone https://github.com/paulairazoqui/vitD-transcriptomic-profiling.git
cd vitD-transcriptomic-profiling
```

### 2. Create and activate the virtual environment

```bash
# Create environment (only once)
python -m venv env

# Activate it
# On Windows (PowerShell)
.\env\Scripts\Activate

# On Linux/Mac
source env/bin/activate

```


### 3. Install the required packages

```bash
pip install -r requirements.txt
```

You can now run the notebooks safely and reproducibly!

### 4. To deactivate the environment

```bash
deactivate
```

---


