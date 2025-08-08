
from django.db import models

from django.db import models

class Compound(models.Model):
    pert_id = models.CharField(max_length=20, primary_key=True)
    cmap_name = models.CharField(max_length=100)
    target = models.TextField(blank=True, null=True)
    moa = models.TextField(blank=True, null=True)
    canonical_smiles = models.TextField(blank=True, null=True)
    inchi_key = models.CharField(max_length=100, blank=True, null=True)
    compound_aliases = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Compound"
        verbose_name_plural = "Compounds"

    def __str__(self):
        return self.cmap_name
    
class CellLine(models.Model):
    cell_id = models.CharField(max_length=40, primary_key=True)  # Ej: MCF7
    cell_type = models.CharField(max_length=50, blank=True, null=True)  # Ej: tumor / normal / pool
    primary_disease = models.CharField(max_length=100, blank=True, null=True)  # Ej: breast cancer
    cell_lineage = models.CharField(max_length=100, blank=True, null=True)  # Ej: breast / lung
    growth_pattern = models.CharField(max_length=50, blank=True, null=True)  # Ej: adherent / suspension / unknown

    class Meta:
        verbose_name = "Cell Line"
        verbose_name_plural = "Cell Lines"

    def __str__(self):
        return self.cell_id

class Signature(models.Model):
    sig_id = models.CharField(max_length=100, primary_key=True)
    pert = models.ForeignKey('Compound', on_delete=models.SET_NULL, null=True, related_name='signatures')
    cell = models.ForeignKey('CellLine', on_delete=models.SET_NULL, null=True, related_name='signatures')

    tas = models.FloatField(blank=True, null=True)
    ss_ngene = models.IntegerField(blank=True, null=True)
    distil_cc_q75 = models.FloatField(blank=True, null=True)

    pert_dose = models.FloatField(blank=True, null=True)
    pert_dose_unit = models.CharField(max_length=20, blank=True, null=True)
    pert_time = models.FloatField(blank=True, null=True)
    pert_time_unit = models.CharField(max_length=10, blank=True, null=True)

    is_exemplar_sig = models.BooleanField(default=False)
    is_null_sig = models.BooleanField(default=False)
    is_ncs_sig = models.BooleanField(default=False)
    qc_pass = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Signature"
        verbose_name_plural = "Signatures"

    def __str__(self):
        return self.sig_id

class Instance(models.Model):
    signature = models.ForeignKey("Signature", on_delete=models.CASCADE, related_name="instances")

    instance_id = models.CharField(max_length=100, unique=True)  # sample_id
    plate_id = models.CharField(max_length=50)                   # det_plate
    well_id = models.CharField(max_length=10)                    # det_well

    count_mean = models.FloatField(null=True, blank=True)
    count_cv = models.FloatField(null=True, blank=True)

    qc_f_logp = models.FloatField(null=True, blank=True)
    qc_iqr = models.FloatField(null=True, blank=True)
    qc_slope = models.FloatField(null=True, blank=True)

    qc_pass = models.BooleanField()

    dyn_range = models.FloatField(null=True, blank=True)
    inv_level_10 = models.FloatField(null=True, blank=True)

    project_code = models.CharField(max_length=20, null=True, blank=True)
    cmap_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Instance"
        verbose_name_plural = "Instances"
        indexes = [
            models.Index(fields=["instance_id"]),
            models.Index(fields=["plate_id"]),
        ]

    def __str__(self):
        return self.instance_id

class Gene(models.Model):
    gene_id = models.IntegerField(primary_key=True)
    gene_symbol = models.CharField(max_length=50, blank=True, null=True)
    ensembl_id = models.CharField(max_length=30, blank=True, null=True)
    gene_title = models.CharField(max_length=255, blank=True, null=True)
    gene_type = models.CharField(max_length=50, blank=True, null=True)
    src = models.CharField(max_length=20, blank=True, null=True)
    feature_space = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Gene"
        verbose_name_plural = "Genes"

    def __str__(self):
        return self.gene_symbol or str(self.gene_id)

class ExpressionMatrixEntry(models.Model):
    gene = models.ForeignKey("Gene", to_field="gene_id", on_delete=models.CASCADE)
    signature = models.ForeignKey("Signature", to_field="sig_id", on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=["gene"]),
            models.Index(fields=["signature"]),
        ]
        verbose_name = "Expression Matrix Entry"
        verbose_name_plural = "Expression Matrix Entries"

    def __str__(self):
        return f"{self.gene.gene_symbol} in {self.signature.sig_id} = {self.value}"
