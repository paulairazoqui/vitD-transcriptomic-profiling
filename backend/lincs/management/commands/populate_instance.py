# backend/lincs/management/commands/populate_instance.py

import re
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from lincs.models import Instance, Signature

FILEPATH_INST = "../raw_data/instinfo_beta.txt"
FILEPATH_SIG  = "../raw_data/siginfo_beta.txt"

CHUNK_INST = 200_000
CHUNK_SIG  = 200_000
BATCH_SIZE = 10_000

# Possible column names across instinfo versions
ALT_INST = {
    "sample_id": ["sample_id", "inst_id", "distil_id"],
    "plate_id": ["det_plate", "plate", "plate_id"],
    "well_id":  ["det_well", "well", "well_id"],
    "count_mean": ["count_mean"],
    "count_cv": ["count_cv"],
    "qc_f_logp": ["qc_f_logp", "qc_f_log_p", "qc_logp_f"],
    "qc_iqr": ["qc_iqr"],
    "qc_slope": ["qc_slope"],
    "qc_pass": ["qc_pass"],
    "dyn_range": ["dyn_range", "dynamic_range"],
    "inv_level_10": ["inv_level_10", "inv_lvl_10", "invariant_level_10"],
    "project_code": ["project_code", "project", "prj_code"],
    "cmap_name": ["cmap_name"],
}

# Possible column names in siginfo
ALT_SIG = {
    "sig_id": ["sig_id"],
    "distil_ids": ["distil_ids", "distil_id_list", "inst_ids"],
}

def pick(columns, alts):
    for c in alts:
        if c in columns:
            return c
    return None

_SPLIT = re.compile(r"[|,;\s]+")

def split_ids(val):
    if pd.isna(val):
        return []
    return [s for s in _SPLIT.split(str(val).strip()) if s]

def build_sig_map(sig_ids, chunk=800):
    """Chunked lookup to avoid SQLite 'too many SQL variables'."""
    sig_map = {}
    ids = list(sig_ids)
    for i in range(0, len(ids), chunk):
        part = ids[i:i+chunk]
        for s in Signature.objects.filter(sig_id__in=part).only("sig_id"):
            sig_map[s.sig_id] = s
    return sig_map

class Command(BaseCommand):
    help = "Populate Instance table from instinfo_beta.txt linking via sample_id ∈ distil_ids in siginfo_beta.txt"

    def handle(self, *args, **options):
        if Instance.objects.exists():
            self.stderr.write(self.style.ERROR("❌ Instance table already populated. Aborting."))
            return

        # Validate we have signatures to link to
        valid_sigs = set(Signature.objects.values_list("sig_id", flat=True))
        if not valid_sigs:
            self.stderr.write(self.style.ERROR("❌ No signatures found. Populate Signature first."))
            return

        total_in = total_written = total_no_sig = total_missing_keys = 0
        chunk_no = 0

        try:
            inst_reader = pd.read_csv(FILEPATH_INST, sep="\t", low_memory=False, chunksize=CHUNK_INST)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {FILEPATH_INST}"))
            return

        for inst_df in inst_reader:
            chunk_no += 1
            cols = set(inst_df.columns)

            # Resolve instinfo columns
            c_sample = pick(cols, ALT_INST["sample_id"])
            c_plate  = pick(cols, ALT_INST["plate_id"])
            c_well   = pick(cols, ALT_INST["well_id"])
            if any(c is None for c in [c_sample, c_plate, c_well]):
                self.stderr.write(self.style.ERROR(f"❌ Missing required columns in instinfo (chunk {chunk_no})."))
                return

            # Keep only relevant columns and normalize names
            opt_map = {k: pick(cols, v) for k, v in ALT_INST.items()}
            use_cols = [c for c in opt_map.values() if c]
            inst_df = inst_df[use_cols].copy()
            inv = {v: k for k, v in opt_map.items() if v}
            inst_df.rename(columns=inv, inplace=True)

            # Basic cleaning
            for c in ["sample_id", "plate_id", "well_id", "project_code", "cmap_name"]:
                if c in inst_df.columns:
                    inst_df[c] = inst_df[c].astype(str).str.strip()

            # Drop rows missing keys
            req_keys = ["sample_id", "plate_id", "well_id"]
            mask = inst_df[req_keys].notna().all(axis=1)
            total_missing_keys += int((~mask).sum())
            inst_df = inst_df[mask]
            total_in += len(inst_df)

            if inst_df.empty:
                self.stdout.write(self.style.WARNING(f"⚠️ Chunk {chunk_no} empty after cleaning."))
                continue

            sample_set = set(inst_df["sample_id"].unique())

            # Build sample_id -> sig_id map by scanning siginfo in chunks
            sample_to_sig = {}
            try:
                sig_reader = pd.read_csv(FILEPATH_SIG, sep="\t", low_memory=False, chunksize=CHUNK_SIG, usecols=None)
            except FileNotFoundError:
                self.stderr.write(self.style.ERROR(f"❌ File not found: {FILEPATH_SIG}"))
                return

            for sig_df in sig_reader:
                scols = set(sig_df.columns)
                c_sig  = pick(scols, ALT_SIG["sig_id"])
                c_dist = pick(scols, ALT_SIG["distil_ids"])
                if not c_sig or not c_dist:
                    self.stderr.write(self.style.ERROR("❌ Missing columns in siginfo (need sig_id & distil_ids)."))
                    return

                sig_df = sig_df[[c_sig, c_dist]].dropna(subset=[c_sig, c_dist]).copy()
                sig_df.rename(columns={c_sig: "sig_id", c_dist: "distil_ids"}, inplace=True)

                for _, r in sig_df.iterrows():
                    sid = r["sig_id"]
                    if sid not in valid_sigs:
                        continue
                    for s in split_ids(r["distil_ids"]):
                        if s in sample_set and s not in sample_to_sig:
                            sample_to_sig[s] = sid

                if len(sample_to_sig) >= len(sample_set):
                    break  # early exit

            # Apply mapping and drop rows without signature
            inst_df["sig_id"] = inst_df["sample_id"].map(sample_to_sig)
            no_sig = inst_df["sig_id"].isna().sum()
            total_no_sig += int(no_sig)
            inst_df = inst_df.dropna(subset=["sig_id"])

            if inst_df.empty:
                self.stdout.write(self.style.WARNING(f"⚠️ Chunk {chunk_no}: 0 rows with sig_id."))
                continue

            # Deduplicate by instance (sample_id is unique in your model)
            before = len(inst_df)
            inst_df = inst_df.drop_duplicates(subset=["sample_id"])
            after = len(inst_df)

            # CHUNKED lookup of signatures to avoid SQLite param limits
            need = inst_df["sig_id"].unique().tolist()
            sig_map = build_sig_map(need, chunk=800)

            # Build objects
            objs = []
            for _, row in inst_df.iterrows():
                sig = sig_map.get(row["sig_id"])
                if not sig:
                    continue
                objs.append(
                    Instance(
                        signature=sig,
                        instance_id=row["sample_id"],
                        plate_id=row["plate_id"],
                        well_id=row["well_id"],
                        count_mean=row.get("count_mean"),
                        count_cv=row.get("count_cv"),
                        qc_f_logp=row.get("qc_f_logp"),
                        qc_iqr=row.get("qc_iqr"),
                        qc_slope=row.get("qc_slope"),
                        qc_pass=bool(row.get("qc_pass", False)),
                        dyn_range=row.get("dyn_range"),
                        inv_level_10=row.get("inv_level_10"),
                        project_code=row.get("project_code"),
                        cmap_name=row.get("cmap_name"),
                    )
                )

                if len(objs) >= BATCH_SIZE:
                    with transaction.atomic():
                        Instance.objects.bulk_create(objs, batch_size=BATCH_SIZE, ignore_conflicts=True)
                    total_written += len(objs)
                    objs.clear()

            if objs:
                with transaction.atomic():
                    Instance.objects.bulk_create(objs, batch_size=BATCH_SIZE, ignore_conflicts=True)
                total_written += len(objs)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Chunk {chunk_no}: {after}/{before} after dedup, total written: {total_written} "
                f"(no sig match in chunk: {int(no_sig)})"
            ))

        # Summary
        self.stdout.write(self.style.SUCCESS(
            "✅ DONE\n"
            f"- Clean rows read:        {total_in}\n"
            f"- Without sig_id (no map):{total_no_sig}\n"
            f"- Missing keys:           {total_missing_keys}\n"
            f"- Written:                {total_written}\n"
            f"Source: {FILEPATH_INST}\n"
            f"Link via: sample_id ∈ distil_ids (siginfo)"
        ))
