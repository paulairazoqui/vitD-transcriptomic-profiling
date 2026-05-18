"""Unit tests for low-risk sensitivity validation helpers."""

from pathlib import Path
import sys

import pytest

pytest.importorskip("pandas")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vitd_utils.sensitivity_validation import (  # noqa: E402
    build_artifact_inventory,
    missing_object_row,
    path_label,
    resolve_registered_artifact,
    validation_detail,
)


@pytest.fixture
def artifact_registry(tmp_path):
    """Return a deterministic artifact registry with mixed path states."""
    preferred_existing = tmp_path / "preferred" / "exists.txt"
    fallback_existing = tmp_path / "fallback" / "exists.txt"
    fallback_only = tmp_path / "fallback" / "fallback_only.txt"
    preferred_existing.parent.mkdir()
    fallback_existing.parent.mkdir()
    preferred_existing.write_text("preferred", encoding="utf-8")
    fallback_existing.write_text("fallback", encoding="utf-8")
    fallback_only.write_text("fallback only", encoding="utf-8")

    return {
        "preferred_exists": {
            "preferred_path": preferred_existing,
            "fallback_path": fallback_existing,
            "artifact_type": "table",
            "status_role": "primary",
        },
        "fallback_exists": {
            "preferred_path": tmp_path / "preferred" / "missing.txt",
            "fallback_path": fallback_existing,
            "artifact_type": "figure",
            "status_role": "secondary",
        },
        "both_missing": {
            "preferred_path": tmp_path / "preferred" / "missing_primary.txt",
            "fallback_path": tmp_path / "fallback" / "missing_fallback.txt",
            "artifact_type": "pickle",
            "status_role": "required",
        },
        "none_preferred_fallback_exists": {
            "preferred_path": None,
            "fallback_path": fallback_only,
            "artifact_type": "csv",
            "status_role": "optional",
        },
    }


def test_path_label_preserves_none():
    assert path_label(None, Path("/project")) is None


def test_path_label_returns_repo_relative_string_for_path_inside_project_root(tmp_path):
    project_root = tmp_path / "repo"
    nested_path = project_root / "results" / "artifact.csv"

    assert Path(path_label(nested_path, project_root)) == Path(
        "results", "artifact.csv"
    )


def test_path_label_returns_absolute_string_for_path_outside_project_root(tmp_path):
    project_root = tmp_path / "repo"
    outside_path = tmp_path / "outside" / "artifact.csv"

    assert path_label(outside_path, project_root) == str(outside_path)


@pytest.mark.parametrize(
    ("messages", "expected"),
    [
        ([], "No issues reported."),
        ([None, "", None, ""], "No issues reported."),
        ([None, "", "first issue", "second issue"], "first issue; second issue"),
        (["count", 3, False], "count; 3; False"),
    ],
)
def test_validation_detail_formats_messages(messages, expected):
    assert validation_detail(messages) == expected


def test_missing_object_row_has_expected_keys_and_failure_status():
    row = missing_object_row("gene sets", "dose_response_gene_sets")

    assert set(row) == {"category", "status", "summary", "detail"}
    assert row["status"] == "FAIL"
    assert row["category"] == "gene sets"
    assert "dose_response_gene_sets" in row["detail"]


def test_missing_object_row_lists_multiple_missing_objects():
    row = missing_object_row("correlations", "score_frame", "comparison_pairs")

    assert "score_frame" in row["detail"]
    assert "comparison_pairs" in row["detail"]


def test_resolve_registered_artifact_reports_missing_registry_entry(tmp_path, artifact_registry):
    path, warning = resolve_registered_artifact("unknown", artifact_registry, tmp_path)

    assert path is None
    assert warning == "unknown: not present in ARTIFACT_REGISTRY"


def test_resolve_registered_artifact_returns_existing_preferred_path(tmp_path, artifact_registry):
    path, warning = resolve_registered_artifact("preferred_exists", artifact_registry, tmp_path)

    assert path == artifact_registry["preferred_exists"]["preferred_path"]
    assert warning is None


def test_resolve_registered_artifact_returns_existing_fallback_when_preferred_missing(
    tmp_path, artifact_registry
):
    path, warning = resolve_registered_artifact("fallback_exists", artifact_registry, tmp_path)

    assert path == artifact_registry["fallback_exists"]["fallback_path"]
    assert warning is None


def test_resolve_registered_artifact_reports_when_neither_path_exists(tmp_path, artifact_registry):
    path, warning = resolve_registered_artifact("both_missing", artifact_registry, tmp_path)

    assert path is None
    assert warning is not None
    assert "both_missing" in warning
    assert "no readable artifact found" in warning
    assert "preferred=" in warning
    assert "missing_primary.txt exists=False" in warning
    assert "fallback=" in warning
    assert "missing_fallback.txt exists=False" in warning


def test_resolve_registered_artifact_returns_fallback_when_preferred_path_is_none(
    tmp_path, artifact_registry
):
    path, warning = resolve_registered_artifact(
        "none_preferred_fallback_exists", artifact_registry, tmp_path
    )

    assert path == artifact_registry["none_preferred_fallback_exists"]["fallback_path"]
    assert warning is None


def test_build_artifact_inventory_reports_expected_columns_order_and_selection(
    tmp_path, artifact_registry
):
    inventory = build_artifact_inventory(artifact_registry, tmp_path)

    assert list(inventory.columns) == [
        "artifact",
        "preferred_exists",
        "fallback_exists",
        "selected_path",
        "artifact_type",
        "status_role",
    ]
    assert inventory["artifact"].tolist() == list(artifact_registry)

    rows = inventory.set_index("artifact").to_dict(orient="index")
    assert rows["preferred_exists"]["preferred_exists"]
    assert rows["preferred_exists"]["fallback_exists"]
    assert Path(rows["preferred_exists"]["selected_path"]) == Path(
        "preferred", "exists.txt"
    )

    assert not rows["fallback_exists"]["preferred_exists"]
    assert rows["fallback_exists"]["fallback_exists"]
    assert Path(rows["fallback_exists"]["selected_path"]) == Path(
        "fallback", "exists.txt"
    )

    assert not rows["both_missing"]["preferred_exists"]
    assert not rows["both_missing"]["fallback_exists"]
    assert Path(rows["both_missing"]["selected_path"]) == Path(
        "preferred", "missing_primary.txt"
    )

    assert not rows["none_preferred_fallback_exists"]["preferred_exists"]
    assert rows["none_preferred_fallback_exists"]["fallback_exists"]
    assert Path(rows["none_preferred_fallback_exists"]["selected_path"]) == Path(
        "fallback", "fallback_only.txt"
    )
    assert rows["none_preferred_fallback_exists"]["artifact_type"] == "csv"
    assert rows["none_preferred_fallback_exists"]["status_role"] == "optional"
