# backend/lincs/management/commands/populate_signature.py

import pandas as pd
from django.core.management.base import BaseCommand
from lincs.models import Signature, Compound, CellLine

class Command(BaseCommand):
    help = "Populate Signature table from siginfo_beta.txt (one-time static load)"

    def handle(self, *args, **options):
        filepath = "../raw_data/siginfo_beta.txt"

        try:
            df = pd.read_csv(filepath, sep="\t", low_memory=False)

            if Signature.objects.exists():
                self.stderr.write(self.style.ERROR("❌ Signature table already populated. Aborting."))
                return

            signatures = []
            for _, row in df.iterrows():
                signatures.append(Signature(
                    sig_id=row["sig_id"],
                    pert=Compound.objects.filter(pert_id=row["pert_id"]).first(),
                    cell=CellLine.objects.filter(cell_id=row["cell_iname"]).first(),

                    tas=row.get("tas", None),
                    ss_ngene=row.get("ss_ngene", None),
                    distil_cc_q75=row.get("cc_q75", None),

                    pert_dose=row.get("pert_dose", None),
                    pert_dose_unit=row.get("pert_dose_unit", None),
                    pert_time=row.get("pert_time", None),
                    pert_time_unit=row.get("pert_time_unit", None),

                    is_exemplar_sig=bool(row.get("is_exemplar_sig", 0)),
                    is_null_sig=bool(row.get("is_null_sig", 0)),
                    is_ncs_sig=bool(row.get("is_ncs_sig", 0)),
                    qc_pass=bool(row.get("qc_pass", 1)),
                ))

            Signature.objects.bulk_create(signatures)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Loaded {len(signatures)} Signatures from {filepath}"
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ File not found: {filepath}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
