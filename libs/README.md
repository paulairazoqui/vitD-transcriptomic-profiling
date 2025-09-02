# External Gene Set Libraries (`libs/`)

This folder contains **external pathway collections** used for enrichment analyses (GSEA / preranked, Enrichr).  
These resources are **not part of the LINCS L1000 raw data**, but are downloaded from the **Molecular Signatures Database (MSigDB)**, Broad Institute / UC San Diego.

## Contents

- `h.all.v2025.1.Hs.symbols.gmt`  
  Hallmark gene sets (H collection).  
  **50 curated gene sets** summarizing key biological processes and well-defined transcriptional programs.  
  Format: HGNC Gene Symbols.  
  Version: MSigDB v2025.1 (Human).

- `c2.cp.reactome.v2025.1.Hs.symbols.gmt`  
  Canonical pathways from **Reactome** (subset of the C2:CP collection).  
  **~1,700 pathways** covering metabolism, signaling, cell cycle, and disease processes.  
  Format: HGNC Gene Symbols.  
  Version: MSigDB v2025.1 (Human).

## Provenance & License

- Source: [MSigDB Collections](https://www.gsea-msigdb.org/gsea/msigdb/) (Broad Institute, UC San Diego).  
- License: requires free academic registration with MSigDB.  
- These files are redistributed here **for local analysis only**. Collaborators should download their own copies directly from MSigDB to comply with licensing.

## Usage

These GMT files are consumed in downstream notebooks (e.g., `04_directed_results.ipynb`) to run:

- **GSEA preranked analyses** (`gseapy.prerank` or fallback implementation).
- **Enrichment dot-plots** summarizing significant pathways across cell lines and vitamin D analogs.

---