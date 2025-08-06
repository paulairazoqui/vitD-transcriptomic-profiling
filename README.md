# 🧬 Vitamin D Transcriptomic Profiling using LINCS L1000 Data

This project explores the transcriptional response of human cell lines to Vitamin D and its analogs, using publicly available gene expression data from the LINCS L1000 dataset (GSE70138).

The goal is to investigate the molecular signatures induced by Vitamin D treatment, identify potential biomarkers, and build predictive models of compound response. This work combines reproducible data processing, exploratory data analysis (EDA), and machine learning, and is designed to be the foundation of a potential scientific preprint or publication.


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


