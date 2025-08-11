# backend/lincs/management/commands/populate_all.py

from django.core.management import call_command
from django.core.management.base import BaseCommand

POPULATE_ORDER = [
    "populate_cellline",
    "populate_compound",
    "populate_signature",
    "populate_instance",
    "populate_gene",
    "populate_expressionmatrixentry"
]

class Command(BaseCommand):
    help = "Run all populate commands in the correct order"

    def handle(self, *args, **options):
        for cmd in POPULATE_ORDER:
            self.stdout.write(self.style.MIGRATE_HEADING(f"🚀 Running {cmd}..."))
            try:
                call_command(cmd)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ {cmd} failed: {e}"))
                self.stderr.write(self.style.ERROR("Stopping populate_all due to error."))
                return
        self.stdout.write(self.style.SUCCESS("🎯 All populate commands completed successfully."))
