# backend/lincs/management/commands/populate_cellline.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from lincs.models import CellLine

CLEAN_NULLS = {"", '""', "unknown", "Unknown", None}

def norm(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    return None if s in CLEAN_NULLS else s

class Command(BaseCommand):
    help = "Populate CellLine table from cellinfo_beta.txt (one-time static load)"

    def handle(self, *args, **options):
        filepath = "../data/raw_data/cellinfo_beta.txt"

        try:
            if CellLine.objects.exists():
                self.stderr.write(self.style.ERROR("❌ CellLine table already populated. Aborting."))
                return

            df = pd.read_csv(filepath, sep="\t", low_memory=False)

            # Columnas que usaremos del archivo
            required = ["cell_iname", "cell_type", "primary_disease", "cell_lineage", "growth_pattern"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                self.stderr.write(self.style.ERROR(f"❌ Missing columns in file: {missing}"))
                return

            # Subset y normalización básica
            df = df[required].copy()
            for col in required:
                df[col] = df[col].map(norm)

            # Dedupe por identificador (cell_iname)
            before = len(df)
            df = df.drop_duplicates(subset=["cell_iname"])
            after = len(df)

            # Build objects (mapeo: cell_id <- cell_iname)
            objs = [
                CellLine(
                    cell_id=row["cell_iname"],
                    cell_type=row["cell_type"],
                    primary_disease=row["primary_disease"],
                    cell_lineage=row["cell_lineage"],
                    growth_pattern=row["growth_pattern"],
                )
                for _, row in df.iterrows()
                if row["cell_iname"]  # evitamos nulos
            ]

            with transaction.atomic():
                CellLine.objects.bulk_create(objs, batch_size=5000)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Loaded {len(objs)} Cell Lines from {filepath} (dedup: {before} → {after})"
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {filepath}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
