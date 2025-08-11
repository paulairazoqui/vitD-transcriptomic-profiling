# backend/lincs/management/commands/populate_compound.py

import pandas as pd
from django.core.management.base import BaseCommand
from lincs.models import Compound

class Command(BaseCommand):
    help = "Populate Compound table from compoundinfo_beta.txt"

    def handle(self, *args, **options):
        filepath = "../raw_data/compoundinfo_beta.txt"

        try:
            df = pd.read_csv(filepath, sep="\t", low_memory=False)

            created_count = 0
            for _, row in df.iterrows():
                obj, created = Compound.objects.update_or_create(
                    pert_id=row["pert_id"],
                    defaults={
                        "cmap_name": row["cmap_name"],
                        "target": row.get("target", None),
                        "moa": row.get("moa", None),
                        "canonical_smiles": row.get("canonical_smiles", None),
                        "inchi_key": row.get("inchi_key", None),
                        "compound_aliases": row.get("compound_aliases", None),
                    }
                )
                if created:
                    created_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Loaded {created_count} new Compounds from {filepath}"
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {filepath}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
