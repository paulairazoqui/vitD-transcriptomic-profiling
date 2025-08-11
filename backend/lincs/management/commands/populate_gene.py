# backend/lincs/management/commands/populate_gene.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from lincs.models import Gene

FILEPATH_GENE = "../raw_data/geneinfo_beta.txt"
CHUNK_SIZE = 50_000
BATCH_SIZE = 10_000

class Command(BaseCommand):
    help = "Populate Gene table from geneinfo_beta.txt"

    def handle(self, *args, **options):
        if Gene.objects.exists():
            self.stderr.write(self.style.ERROR("❌ Gene table already populated. Aborting."))
            return

        total_in = total_written = 0
        chunk_no = 0

        try:
            reader = pd.read_csv(FILEPATH_GENE, sep="\t", low_memory=False, chunksize=CHUNK_SIZE)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {FILEPATH_GENE}"))
            return

        for df in reader:
            chunk_no += 1
            cols_needed = ["gene_id", "gene_symbol", "ensembl_id", "gene_title",
                           "gene_type", "src", "feature_space"]

            missing = [c for c in cols_needed if c not in df.columns]
            if missing:
                self.stderr.write(self.style.ERROR(f"❌ Missing required columns: {missing}"))
                return

            # Clean strings
            for col in ["gene_symbol", "ensembl_id", "gene_title", "gene_type", "src", "feature_space"]:
                df[col] = df[col].astype(str).replace({"nan": None, "": None}).str.strip()

            # Drop duplicates by gene_id
            before = len(df)
            df = df.drop_duplicates(subset=["gene_id"])
            after = len(df)
            total_in += after

            objs = [
                Gene(
                    gene_id=int(row["gene_id"]),
                    gene_symbol=row["gene_symbol"] if row["gene_symbol"] else None,
                    ensembl_id=row["ensembl_id"] if row["ensembl_id"] else None,
                    gene_title=row["gene_title"] if row["gene_title"] else None,
                    gene_type=row["gene_type"] if row["gene_type"] else None,
                    src=row["src"] if row["src"] else None,
                    feature_space=row["feature_space"] if row["feature_space"] else None,
                )
                for _, row in df.iterrows()
            ]

            # Bulk insert in chunks
            for i in range(0, len(objs), BATCH_SIZE):
                with transaction.atomic():
                    Gene.objects.bulk_create(objs[i:i+BATCH_SIZE], batch_size=BATCH_SIZE, ignore_conflicts=True)
                total_written += len(objs[i:i+BATCH_SIZE])

            self.stdout.write(self.style.SUCCESS(
                f"✅ Chunk {chunk_no}: {after}/{before} after dedup, total written so far: {total_written}"
            ))

        # Summary
        self.stdout.write(self.style.SUCCESS(
            "✅ DONE\n"
            f"- Rows read (after cleaning & dedup): {total_in}\n"
            f"- Total written: {total_written}\n"
            f"Source: {FILEPATH_GENE}"
        ))
