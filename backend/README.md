# Backend (Track 4: Dashboard/backend support)

This directory contains Track 4 infrastructure for backend/dashboard support in the future vitamin D transcriptomics platform.

It provides Django and database infrastructure for storing and querying LINCS metadata and project subset expression values.

Major contents include:
- `manage.py`
- `vitd_project/`
- `lincs` app
- models
- migrations
- management commands

For full schema and database logic details, see `../docs/database_documentation.md`.

Population and validation workflows include:
- `populate_all`: populates database tables from project data inputs and processing outputs.
- `validate_db`: runs validation checks to confirm database consistency and expected integrity constraints.

Operational boundaries:
- Supports storage, query, validation, and future platform development work.
- Does not itself generate manuscript claims or manuscript figures.
- Manuscript-confirmatory analyses remain notebook/results driven.
