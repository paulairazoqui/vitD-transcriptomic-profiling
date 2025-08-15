# backend/lincs/management/commands/populate_expressionmatrixentry.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from lincs.models import ExpressionMatrixEntry, Gene, Signature

FILEPATH_MATRIX = "../data/processed_data/vitD_expression_matrix.csv"
CHUNK_SIZE = 1_000  # rows (genes) per chunk to keep memory under control
BATCH_SIZE = 5_000  # bulk_create batch size

class Command(BaseCommand):
    help = "Populate ExpressionMatrixEntry table from processed expression matrix CSV"

    def handle(self, *args, **options):
        if ExpressionMatrixEntry.objects.exists():
            self.stderr.write(self.style.ERROR("❌ ExpressionMatrixEntry table already populated. Aborting."))
            return

        # Pre-load gene and signature sets for fast lookup
        self.stdout.write("🔍 Loading Gene and Signature IDs into memory...")
        valid_genes = set(Gene.objects.values_list("gene_id", flat=True))
        valid_sigs = {s: s for s in Signature.objects.values_list("sig_id", flat=True)}

        if not valid_genes:
            self.stderr.write(self.style.ERROR("❌ No genes found. Populate Gene first."))
            return
        if not valid_sigs:
            self.stderr.write(self.style.ERROR("❌ No signatures found. Populate Signature first."))
            return

        self.stdout.write("📄 Reading matrix file...")
        try:
            reader = pd.read_csv(FILEPATH_MATRIX, chunksize=CHUNK_SIZE)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {FILEPATH_MATRIX}"))
            return

        total_written = 0
        chunk_no = 0

        for df in reader:
            chunk_no += 1

            if "rid" not in df.columns:
                self.stderr.write(self.style.ERROR("❌ Missing 'rid' column for gene_id."))
                return

            # Ensure correct dtypes
            df["rid"] = pd.to_numeric(df["rid"], errors="coerce").astype("Int64")
            df = df.dropna(subset=["rid"])

            objs = []
            for _, row in df.iterrows():
                gene_id = int(row["rid"])
                if gene_id not in valid_genes:
                    continue  # skip genes not in DB

                for sig_id, val in row.items():
                    if sig_id == "rid":
                        continue
                    if sig_id not in valid_sigs:
                        continue  # skip sigs not in DB

                    # Ignore NaN values
                    if pd.isna(val):
                        continue

                    objs.append(
                        ExpressionMatrixEntry(
                            gene_id=gene_id,
                            signature_id=sig_id,
                            value=float(val)
                        )
                    )

                    # Bulk insert per batch
                    if len(objs) >= BATCH_SIZE:
                        with transaction.atomic():
                            ExpressionMatrixEntry.objects.bulk_create(
                                objs, batch_size=BATCH_SIZE, ignore_conflicts=True
                            )
                        total_written += len(objs)
                        objs.clear()

            # Insert any remaining objects for this chunk
            if objs:
                with transaction.atomic():
                    ExpressionMatrixEntry.objects.bulk_create(
                        objs, batch_size=BATCH_SIZE, ignore_conflicts=True
                    )
                total_written += len(objs)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Chunk {chunk_no} processed. Total written so far: {total_written}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"🎯 DONE. Total ExpressionMatrixEntry written: {total_written}"
        ))
