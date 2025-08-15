# 📂 Raw Data Directory

This folder contains a curated subset of raw files from the [CLUE LINCS2020 dataset](https://clue.io/data/CMap2020#LINCS2020), part of the Connectivity Map (CMap) project. The selection includes metadata and a single expression matrix required to analyze the transcriptomic effects of Vitamin D and its analogs in human cell lines.

These files were downloaded manually from the official source and are kept in their original format.

### Raw Data Files

| File | Size | SHA256 |
|------|------|--------|
| `cellinfo_beta.txt` | ~0.04 MB | `D26A08F7F290F6A94BFF593CDEA4DCFC3FE17177E05593CD381CB65AEBC63FC2` |
| `compoundinfo_beta.txt` | ~4.42 MB | `A71FCA6DE41DCC46A5063858BE7E04155F3C09832C8B3FB35814F03DB8D9FDFF` |
| `geneinfo_beta.txt` | ~1.09 MB | `E739D06BAD42FF9285C00B778E65D8999425062A3375CC7E7CDAB0E7154490B5` |
| `instinfo_beta.txt` | ~643.58 MB | `2676189E8EA4A4CFDAFC6C7E1B9F1776F4459EBFE4F79F6A736C3F3A732D3249` |
| `siginfo_beta.txt` | ~180 MB | `1A38D7EA2A804BE79804AF4A27AFF9F2537AF8F13D3C8AF1FDC1FEF780F40201` |

<details>
<summary><strong>Verification hashes (MD5 vs official)</strong></summary>

| File | MD5 (official CLUE) | MD5 (calculated) | Status |
|------|----------------------|------------------|--------|
| `cellinfo_beta.txt` | `c4686b4bcd2bad8fa64e229932c8d486` | `C4686B4BCD2BAD8FA64E229932C8D486` | ✅ Match |
| `compoundinfo_beta.txt` | `bf8e3a15ad026b47903c98d625195d24` | `BF8E3A15AD026B47903C98D625195D24` | ✅ Match |
| `geneinfo_beta.txt` | `45c725d17ce6c377f1e7de07b821a5f0` | `45C725D17CE6C377F1E7DE07B821A5F0` | ✅ Match |
| `instinfo_beta.txt` | `e1edf4e306cebcc6d3e061b5a50114dc` | `E1EDF4E306CEBCC6D3E061B5A50114DC` | ✅ Match |
| `siginfo_beta.txt` | `ab609fc04fab21180b07833119d1c7b6` | `AB609FC04FAB21180B07833119D1C7B6` | ✅ Match |

</details>
<br>

> ℹ️ We publish **SHA256** as the primary integrity hash. **MD5** hashes are shown only to cross-check with the values provided by CLUE.

---

## Expression Matrix

Only one expression matrix was downloaded, containing Level 5 moderated z-scores for compound perturbagens:

| File                                    | Description                                                                                   | Size   | SHA256                                                             |
| --------------------------------------- | --------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| `level5_beta_trt_cp_n720216x12328.gctx` | Moderated, replicate-collapsed z-scores for ~720,000 compound signatures across 12,328 genes | ~33 GB | `FBB04A94D8AA8A4FA6DAF01F7D94DCD938FB9B7937730F81BFBA3D8D0F1472A8` |

<details>
<summary><strong>Verification hash (MD5 vs official)</strong></summary>

| MD5 (official CLUE) | MD5 (calculated) | Status |
| ------------------- | ---------------- | ------ |
| `9a82806e2aba6ec2a866cba77bd57fda` | `9A82806E2ABA6EC2A866CBA77BD57FDA` | ✅ Match |

</details>
<br>

> ⚠️ Other available GCTX files were excluded to reduce storage requirements and focus the analysis on compounds relevant to our research question.

## 🕒 Version and Download Timestamp
All files listed above were manually downloaded in August 2025.

At the time of download, the most recent available version of the dataset was:

CMAP LINCS 2020
- Updated: November 23, 2021
- Created: November 20, 2020
- Source: [https://clue.io/data/CMap2020#LINCS2020](https://clue.io/data/CMap2020#LINCS2020)

This ensures that all analyses are based on the latest officially published release of the LINCS L1000 dataset available as of that date.

## 📥 How to Reproduce This Folder

All files were downloaded from:  
🔗 [https://clue.io/data/CMap2020#LINCS2020](https://clue.io/data/CMap2020#LINCS2020)  
➡️ Section: *LINCS2020 – L1000 data*

**Alternative access (manual navigation)**  

1. Go to: 🔗 [https://clue.io/data](https://clue.io/data)  
2. In the dataset list, locate **Expanded CMap LINCS Resource 2020 (CMap2020)**.  
3. Click to expand it and select **CMAP LINCS 2020** (Completed – 11/23/21).  
4. Download the following files:  
   - `cellinfo_beta.txt`  
   - `compoundinfo_beta.txt`  
   - `geneinfo_beta.txt`  
   - `instinfo_beta.txt`  
   - `siginfo_beta.txt`  
   - `level5_beta_trt_cp_n720216x12328.gctx`  

Place the downloaded files into the `raw_data` directory without renaming them.

> ⚠️ **Do not rename the files.** All scripts and notebooks in this project rely on the original filenames provided by CLUE. Maintaining the exact filenames ensures full reproducibility of the analysis pipeline.

> 🗃️ Due to their large size, these files are not tracked in the GitHub repository. Please refer to the project documentation for guidance on preprocessing and analysis.

