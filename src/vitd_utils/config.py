# src/vitd_utils/config.py

"""
Global configuration for the Vitamin D transcriptomic profiling project.

This file centralizes all constants, default parameters, and paths
used across notebooks and utility modules. By keeping them here,
we ensure reproducibility and make it easy to update project-wide settings.
"""

from pathlib import Path

# ---------------------------------------------------------------------
# Random seeds and reproducibility
# ---------------------------------------------------------------------
SEED = 0
RANDOM_STATE = 0

# ---------------------------------------------------------------------
# Project directories
# ---------------------------------------------------------------------
# Base paths are defined relative to the repository root.
# Adjust these if the project structure changes.
ROOT_DIR = Path(__file__).resolve().parents[2]   # go two levels up from src/vitd_utils
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"
LIB_DIR = ROOT_DIR / "libs"   # location for .gmt libraries (MSigDB)

# Ensure that results/figures directories exist at runtime
FIG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Core-gene and consensus parameters
# ---------------------------------------------------------------------
N_TOP = 50        # window size for per-context top/bottom genes (vote-count)
VOTE_MIN = 2      # minimum contexts to call a gene 'consensus'
CORE_UP_N = 42    # default size of consensus UP genes (from Section 3)
CORE_DN_N = 35    # default size of consensus DOWN genes

# ---------------------------------------------------------------------
# Enrichment analysis parameters
# ---------------------------------------------------------------------
TOP_LIST = 200        # number of genes per extreme for Enrichr UP/DOWN lists
MIN_SIGS = 2          # minimum number of signatures to build a mean profile
ENR_TOP_PATHWAYS = 12 # number of top pathways to display in dotplots
PERM_N = 400          # default number of permutations for GSEA-like enrichment
CHUNK_PERMS = 50      # number of permutations per batch (resumable runs)

# Default libraries: Hallmarks and Reactome (symbol-based GMTs)
GSEA_LIBRARIES = {
    "Hallmarks": str(LIB_DIR / "h.all.v2025.1.Hs.symbols.gmt"),
    "Reactome": str(LIB_DIR / "c2.cp.reactome.v2025.1.Hs.symbols.gmt"),
}

# ---------------------------------------------------------------------
# Output control
# ---------------------------------------------------------------------
SAVE_FIGS = True   # change to True to automatically save figures
SAVE_TABLES = False # optional: set True to export enrichment tables
