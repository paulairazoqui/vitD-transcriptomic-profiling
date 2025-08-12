# backend/lincs/management/commands/validate_db.py

import random
from django.core.management.base import BaseCommand
from django.db.models import Count
from lincs.models import (
    CellLine, Compound, Signature, Instance, Gene, ExpressionMatrixEntry
)

class Command(BaseCommand):
    help = "Quick validation of DB counts, samples, FK consistency and matrix shape"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("📊 Counts"))
        counts = {
            "CellLine": CellLine.objects.count(),
            "Compound": Compound.objects.count(),
            "Signature": Signature.objects.count(),
            "Instance": Instance.objects.count(),
            "Gene": Gene.objects.count(),
            "ExpressionMatrixEntry": ExpressionMatrixEntry.objects.count(),
        }
        for k, v in counts.items():
            self.stdout.write(f"- {k}: {v:,}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n🔎 Random samples"))
        def sample_qs(qs, fields, n=3):
            ids = list(qs.values_list('pk', flat=True)[:1000])
            if not ids:
                return
            pick = random.sample(ids, min(n, len(ids)))
            for obj in qs.filter(pk__in=pick):
                line = " | ".join(f"{f}={getattr(obj, f, None)}" for f in fields)
                self.stdout.write(f"  • {line}")

        sample_qs(CellLine.objects.all(), ["cell_id", "cell_type", "primary_disease"])
        sample_qs(Compound.objects.all(), ["pert_id", "cmap_name"])
        sample_qs(Signature.objects.all(), ["sig_id", "pert_id", "cell_id"])
        sample_qs(Instance.objects.all(), ["instance_id", "plate_id", "well_id", "signature_id"])
        sample_qs(Gene.objects.all(), ["gene_id", "gene_symbol", "feature_space"])
        sample_qs(ExpressionMatrixEntry.objects.all(), ["gene_id", "signature_id", "value"])

        self.stdout.write(self.style.MIGRATE_HEADING("\n🔗 FK consistency checks"))
        orphans_sig = Instance.objects.filter(signature__isnull=True).count()
        orphans_gene = ExpressionMatrixEntry.objects.filter(gene__isnull=True).count()
        orphans_sig_in_expr = ExpressionMatrixEntry.objects.filter(signature__isnull=True).count()
        self.stdout.write(f"- Instances without Signature: {orphans_sig}")
        self.stdout.write(f"- ExprEntries without Gene: {orphans_gene}")
        self.stdout.write(f"- ExprEntries without Signature: {orphans_sig_in_expr}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n🧮 Matrix shape check"))
        # cuántas signatures aparecen en la matriz (columnas del CSV que insertaste)
        sig_in_matrix = ExpressionMatrixEntry.objects.values("signature_id").distinct().count()
        genes = counts["Gene"]
        expr = counts["ExpressionMatrixEntry"]
        expected = genes * sig_in_matrix
        ok = "OK ✅" if expr == expected else "MISMATCH ❌"
        self.stdout.write(
            f"- Unique signatures in matrix: {sig_in_matrix:,}\n"
            f"- Genes: {genes:,}\n"
            f"- Expected entries: {expected:,}\n"
            f"- Actual entries:   {expr:,}  => {ok}"
        )

        self.stdout.write(self.style.MIGRATE_HEADING("\n📌 Extra sanity checks"))
        # ¿Cada signature de la matriz tiene exactamente #genes filas?
        bad_sigs = (
            ExpressionMatrixEntry.objects
            .values("signature_id")
            .annotate(c=Count("id"))
            .exclude(c=genes)
            .count()
        )
        self.stdout.write(f"- Signatures with incomplete rows (≠ {genes} genes): {bad_sigs}")

        # ¿Cada gene tiene exactamente #sig_in_matrix filas?
        bad_genes = (
            ExpressionMatrixEntry.objects
            .values("gene_id")
            .annotate(c=Count("id"))
            .exclude(c=sig_in_matrix)
            .count()
        )
        self.stdout.write(f"- Genes with incomplete columns (≠ {sig_in_matrix} signatures): {bad_genes}")

        self.stdout.write(self.style.SUCCESS("\n🎯 Validation finished."))
