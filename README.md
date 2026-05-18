# Gene-level variability, pathway-level convergence: a systems view of vitamin D signaling

This repository is a vitamin D transcriptomics research repository centered on the submitted manuscript **"Gene-level variability, pathway-level convergence: a systems view of vitamin D signaling"**. It contains the manuscript-associated analysis track together with exploratory notebooks, supporting analyses, dashboard-related utilities, and development materials that document the broader research workflow.

The manuscript analyzes vitamin D-related perturbational transcriptomic signatures from **LINCS L1000**. The validated manuscript scope includes **258 perturbational signatures**, **5 human cell lines** (**A549, HA1E, MCF7, PC3, U2OS**), **7 vitamin D-related compounds**, and **24-hour perturbations**. Analyses focus on gene-level variability, Hallmark pathway enrichment, a consensus transcriptional core, the `core_score` metric, dose-response analysis, and VDR-axis analysis.

## Repository structure

```text
.
├── README.md                  # Repository overview and reproducibility guide
├── docs/                      # Manuscript context and supporting documentation
├── notebooks/                 # Analysis notebooks used for data processing, analysis, and figure generation
├── src/vitd_utils/            # Shared analysis utilities and configuration
├── data/                      # Raw, processed, exported, and dashboard-ready data files
├── results/                   # Generated tables, enrichment outputs, and figures
├── enrichment/                # External enrichment-related input files and supporting analysis
├── images/                    # Repository-level images and schematic files
├── backend/                   # Dashboard/database support code
├── libs/                      # Local library notes
└── requirements.txt           # Python dependencies
```

## Analysis organization

The repository separates the central manuscript-associated track from broader exploratory and development work.

### Manuscript-associated analysis track

The primary manuscript analyses are organized as notebooks in `notebooks/`:

1. `01_filtering.ipynb` — LINCS L1000 subset definition and filtering.
2. `02_EDA.ipynb` and `03_EDA_subset.ipynb` — exploratory analyses of the full and curated subsets.
3. `04_directed_results.ipynb` — directed manuscript analyses, including the consensus transcriptional core, `core_score`, dose-response analysis, and Hallmark pathway enrichment.
4. `06_functional_context.ipynb` — functional context for enrichment results.
5. `07_statistical_modeling_core_score.ipynb` — statistical modeling of the `core_score` metric.

Generated manuscript-associated outputs are organized under `results/`, with figures in `results/figures/`, enrichment outputs in `results/enrichment/`, and tabular outputs in `results/dfs/`.

### Exploratory, development, and supporting materials

Additional notebooks and files document exploratory analyses, supporting checks, analysis variants, dashboard-ready data, and database/dashboard infrastructure. These materials are part of the broader research workflow and should be interpreted according to their local notebook context rather than as additional manuscript claims.

## Reproducibility

The repository is intended to support transparent inspection and rerunning of the manuscript-associated analyses while preserving the broader exploratory and development record.

Basic setup:

```bash
git clone https://github.com/paulairazoqui/vitD-transcriptomic-profiling
cd vitD-transcriptomic-profiling
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To reproduce the manuscript-associated track, run the relevant notebooks from `notebooks/` in numerical order, starting with `01_filtering.ipynb`. Shared paths and configuration are defined in `src/vitd_utils/`, and analysis outputs are written to the organized `data/` and `results/` subdirectories. Exploratory notebooks, dashboard utilities, and supporting materials can be rerun or inspected independently where their dependencies and local context apply.

## Data source

The transcriptomic perturbation data are from **LINCS L1000**. The curated manuscript dataset contains **258 perturbational signatures** from **A549, HA1E, MCF7, PC3, and U2OS** cells treated for **24 hours** with **7 vitamin D-related compounds**.

## Citation

If you use this repository, please cite the submitted manuscript:

> Gene-level variability, pathway-level convergence: a systems view of vitamin D signaling.
