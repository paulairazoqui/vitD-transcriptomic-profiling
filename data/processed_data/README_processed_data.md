# 📂 Processed Data Directory

This directory stores **intermediate processed data** generated during the transformation of the LINCS L1000 raw dataset into the final project-specific subset.

## Purpose
The files in this folder are **reproducible intermediate outputs** created after applying filtering, normalization, and other preprocessing steps to the raw data.  
They serve as the bridge between:
1. The original **raw data** in `data/raw_data/`
2. The **final exports** in `data/exports/`

## File Types (Example Outputs)
- Filtered metadata tables (e.g., `siginfo_vitD_filtered.csv`)
- Identifier lists for selected signatures (e.g., `sig_ids_vitD_filtered.txt`)
- Reduced or subsetted expression matrices

## Reproducibility
- **Not versioned in Git** — excluded via `.gitignore` to prevent large file storage in the repository.
- All files in this directory can be **fully regenerated** from:
  1. The raw data in `data/raw_data/`
  2. The processing scripts in `backend/lincs/management/commands/`

## Naming Convention

```text
<entity>_vitD_subset.csv           # Filtered subset of a given entity (e.g., instinfo, geneinfo)
sig_ids_vitD_filtered.txt          # Signature IDs after filtering by project criteria
vitD_expression_matrix.csv         # Subsetted expression matrix (gene-level)
```

## Notes
- Column definitions and schema are documented in [`docs/database_documentation.md`](../../docs/database_documentation.md).
- This folder should remain **empty** until processed data are generated locally.
- Do **not** manually edit files in this directory; always regenerate using the official scripts.
