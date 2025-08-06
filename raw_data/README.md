# 📁 Raw Data: LINCS L1000 Subset for Vitamin D Transcriptomic Profiling

This folder contains a curated subset of raw files from the [CLUE LINCS2020 dataset](https://clue.io/data/CMap2020#LINCS2020), part of the Connectivity Map (CMap) project. The selection includes metadata and a single expression matrix required to analyze the transcriptomic effects of Vitamin D and its analogs in human cell lines.

These files were downloaded manually from the official source and are kept in their original format.

## 📄 Metadata Files

- `cellinfo_beta.txt`: Cell line metadata.
- `compoundinfo_beta.txt`: Compound-level metadata.
- `geneinfo_beta.txt`: Gene annotations (landmark + inferred genes).
- `instinfo_beta.txt`: Signature-level metadata (perturbation, time, dose, etc.).
- `siginfo_beta.txt`: Supplementary metadata for signatures.

## 📊 Expression Matrix

Only one expression matrix was downloaded, containing Level 5 moderated z-scores for compound perturbagens:

- `level5_beta_trt_cp_n720216x12328.gctx`: Moderated, replicate-collapsed z-scores for ~720,000 compound signatures across 12,328 genes.

> ⚠️ Other available GCTX files were excluded to reduce storage requirements and focus the analysis on compounds relevant to our research question.

## 📥 How to Reproduce This Folder

All files were downloaded from:  
🔗 https://clue.io/data/CMap2020#LINCS2020  
➡️ Section: *LINCS2020 - L1000 data*

To replicate this data structure:
1. Visit the URL above.
2. Download only the files listed here.
3. Place them in the `raw_data` directory.

> ⚠️ **Do not rename the files.** All scripts and notebooks in this project rely on the original filenames provided by CLUE. Maintaining the exact filenames ensures full reproducibility of the analysis pipeline.

> 🗃️ Due to their large size, these files are not tracked in the GitHub repository. Please refer to the project documentation for guidance on preprocessing and analysis.
