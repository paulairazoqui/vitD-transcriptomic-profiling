# backend/lincs/management/commands/export_subset.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Q
from lincs.models import Compound, CellLine, Signature, ExpressionMatrixEntry, Gene

# ---------- Fixed project parameters ----------
DEFAULT_KEYWORDS = [
    "calcitriol", "calcipotriol", "maxacalcitol", "seocalcitol",
    "ercalcitriol", "tacalcitol", "paricalcitol",
]
PROJECT_CELLS = ["PC3", "MCF7", "A549", "U2OS", "HA1E"]
PERT_TIME = 24  # hours


class Command(BaseCommand):
    help = (
        "Export the fixed project subset (vitamin D/analogs @24h in "
        "PC3/MCF7/A549/U2OS/HA1E): full metadata + expression matrices."
    )

    def add_arguments(self, parser):
        parser.add_argument("--outdir", type=str, default="../data/exports", help="Output directory.")
        parser.add_argument("--long", action="store_true", help="Also export long/tidy expression table.")
        parser.add_argument("--limit_sigs", type=int, default=None, help="Optional cap on number of signatures.")
        parser.add_argument("--landmark_only", action="store_true",
                            help="Keep only genes with feature_space='landmark' (the 978).")
        parser.add_argument("--with_symbol_matrix", action="store_true",
                            help="Also export a symbol-averaged matrix (gene_symbol rows).")

    def handle(self, *args, **opts):
        outdir = opts["outdir"]
        limit = opts["limit_sigs"]
        lm_only = opts["landmark_only"]
        export_symbol_matrix = opts["with_symbol_matrix"]

        # Ensure output directory exists
        os.makedirs(outdir, exist_ok=True)

        # ---------- 1) Select compounds by vitamin D keywords ----------
        q = Q()
        for k in DEFAULT_KEYWORDS:
            q |= Q(cmap_name__icontains=k)
        comp_ids = list(Compound.objects.filter(q).values_list("pert_id", flat=True))
        if not comp_ids:
            self.stderr.write(self.style.ERROR("No compounds matched the vitamin D keywords."))
            return

        # ---------- 2) Select signatures (fixed time + fixed cell lines) ----------
        sig_qs = (
            Signature.objects
            .filter(pert_id__in=comp_ids, pert_time=PERT_TIME, cell_id__in=PROJECT_CELLS)
            .order_by("sig_id")
        )
        if limit:
            sig_qs = sig_qs[:limit]

        # Export FULL signature metadata (all model fields), subset rows only
        sig_full = pd.DataFrame(list(sig_qs.values()))
        if sig_full.empty:
            self.stderr.write(self.style.ERROR(
                "No signatures found after applying fixed filters (compounds + 24h + cell lines)."
            ))
            return

        # Persist full Signatures metadata
        sig_path = os.path.join(outdir, "subset_signatures_meta.csv")
        sig_full.to_csv(sig_path, index=False)
        self.stdout.write(self.style.SUCCESS(f"✅ Signatures selected: {len(sig_full)}"))
        self.stdout.write(f"📝 Signatures (full cols) → {sig_path}")

        # Convenience: extract IDs for downstream joins/filters
        sig_ids = sig_full["sig_id"].tolist()
        used_pert_ids = sig_full["pert_id"].dropna().unique().tolist()
        used_cell_ids = sig_full["cell_id"].dropna().unique().tolist()

        # ---------- 3) Export FULL compounds and cell lines referenced by the subset ----------
        comp_full = pd.DataFrame(list(Compound.objects.filter(pert_id__in=used_pert_ids).values()))
        comp_path = os.path.join(outdir, "subset_compounds_meta.csv")
        comp_full.to_csv(comp_path, index=False)
        self.stdout.write(f"📝 Compounds (full cols) → {comp_path}")

        cell_full = pd.DataFrame(list(CellLine.objects.filter(cell_id__in=used_cell_ids).values()))
        cell_path = os.path.join(outdir, "subset_cell_lines_meta.csv")
        cell_full.to_csv(cell_path, index=False)
        self.stdout.write(f"📝 Cell lines (full cols) → {cell_path}")

        # ---------- 4) Export FULL gene metadata for genes present in the subset ----------
        # Get distinct gene_ids present in ExpressionMatrixEntry for selected signatures
        genes_in_subset = list(
            ExpressionMatrixEntry.objects
            .filter(signature_id__in=sig_ids)
            .values_list("gene_id", flat=True)
            .distinct()
        )
        # Full columns from Gene, limited to genes present in this subset
        gene_df = pd.DataFrame(list(Gene.objects.filter(gene_id__in=genes_in_subset).values()))
        genes_meta_path = os.path.join(outdir, "subset_genes_meta.csv")
        gene_df.sort_values("gene_id").to_csv(genes_meta_path, index=False)
        self.stdout.write(f"📝 Genes (full cols) → {genes_meta_path}")

        # Quick maps for symbol and feature_space
        symbol_map = dict(gene_df[["gene_id", "gene_symbol"]].values)
        fs_map = dict(gene_df[["gene_id", "feature_space"]].values)

        # ---------- 5) Load expression and (optionally) filter to landmark genes ----------
        expr_qs = (
            ExpressionMatrixEntry.objects
            .filter(signature_id__in=sig_ids)
            .values("gene_id", "signature_id", "value")
        )
        expr_df = pd.DataFrame(list(expr_qs.iterator()))
        if expr_df.empty:
            self.stderr.write(self.style.ERROR("No expression entries found for selected signatures."))
            return

        if lm_only:
            expr_df = expr_df[expr_df["gene_id"].map(fs_map).fillna("").str.lower().eq("landmark")]
            self.stdout.write("🔧 Applied landmark-only filter (feature_space=landmark).")

        # Attach helpful columns for auditability (not used in pivot keys)
        expr_df["gene_symbol"] = expr_df["gene_id"].map(symbol_map).fillna(expr_df["gene_id"].astype(str))
        expr_df["feature_space"] = expr_df["gene_id"].map(fs_map)

        # Diagnostics: duplicated (gene_id, signature_id) pairs
        dup_count = expr_df.duplicated(["gene_id", "signature_id"]).sum()
        self.stdout.write(f"🔎 Collapsed duplicate pairs: {dup_count:,}")

        # Aggregate duplicates at (gene_id, signature_id) level (mean is standard)
        expr_agg = (
            expr_df.groupby(["gene_id", "signature_id"], as_index=False)
                   .agg(value=("value", "mean"),
                        gene_symbol=("gene_symbol", "first"),
                        feature_space=("feature_space", "first"))
        )

        # ---------- 6) Pivot to wide (rows=gene_id, cols=sig_id) ----------
        wide_gid = expr_agg.pivot(index="gene_id", columns="signature_id", values="value")
        # Keep signature order and sort genes for reproducibility
        wide_gid = wide_gid.reindex(columns=sig_ids).sort_index()

        # Insert non-numeric headers (drop them before ML)
        symbol_series = pd.Series(wide_gid.index, index=wide_gid.index, dtype=object).map(
            lambda gid: symbol_map.get(gid, str(gid))
        )
        fs_series = pd.Series(wide_gid.index, index=wide_gid.index, dtype=object).map(lambda gid: fs_map.get(gid))
        wide_gid.insert(0, "feature_space", fs_series)
        wide_gid.insert(0, "gene_symbol", symbol_series)

        suffix = "_lm" if lm_only else ""
        wide_gid_path = os.path.join(outdir, f"subset_expression_wide_gene_id{suffix}.csv")
        wide_gid.to_csv(wide_gid_path)
        self.stdout.write(
            f"📦 Wide (gene_id) → {wide_gid_path} (shape {wide_gid.shape[0]}×{wide_gid.shape[1]-2})"
        )

        # ---------- 7) Optional: symbol-averaged matrix (rows=gene_symbol) ----------
        if export_symbol_matrix:
            # Average rows that share the same gene_symbol (feature_space is not defined after averaging)
            wide_symbol = (
                wide_gid.drop(columns=["gene_symbol", "feature_space"])
                        .assign(gene_symbol=wide_gid["gene_symbol"].values)
                        .groupby("gene_symbol")
                        .mean(numeric_only=True)
                        .reindex(columns=sig_ids)
                        .sort_index()
            )
            wide_symbol_path = os.path.join(outdir, f"subset_expression_wide_symbol{suffix}.csv")
            wide_symbol.to_csv(wide_symbol_path)
            self.stdout.write(
                f"📦 Wide (gene_symbol, averaged) → {wide_symbol_path} "
                f"(shape {wide_symbol.shape[0]}×{wide_symbol.shape[1]})"
            )

        # ---------- 8) Optional: long/tidy export ----------
        if opts["long"]:
            long_df = expr_agg[["gene_id", "gene_symbol", "feature_space", "signature_id", "value"]].copy()
            long_df = long_df.sort_values(["gene_id", "signature_id"]).reset_index(drop=True)
            long_path = os.path.join(outdir, f"subset_expression_long{suffix}.csv")
            long_df.to_csv(long_path, index=False)
            self.stdout.write(f"📦 Long (deduped) → {long_path} (rows {len(long_df):,})")

        # ---------- 9) Final summary ----------
        lm_msg = " + LANDMARK-ONLY" if lm_only else ""
        sym_msg = " + SYMBOL-MATRIX" if export_symbol_matrix else ""
        self.stdout.write(self.style.SUCCESS(
            f"🎯 Export finished{lm_msg}{sym_msg}. "
            f"Filters: vitamin D keywords + 24h + PC3/MCF7/A549/U2OS/HA1E."
        ))
