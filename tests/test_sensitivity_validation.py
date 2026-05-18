"""Unit tests for low-risk sensitivity validation helpers."""

from pathlib import Path
import sys

import pytest

pd = pytest.importorskip("pandas")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vitd_utils.sensitivity_validation import (  # noqa: E402
    build_artifact_inventory,
    gene_set_overlap_row,
    missing_object_row,
    path_label,
    resolve_registered_artifact,
    score_correlations,
    validation_detail,
)


def assert_missing(value):
    assert pd.isna(value)


def test_score_correlations_reports_expected_columns_order_for_numeric_input():
    frame = pd.DataFrame({"score_a": [1, 2, 3], "score_b": [2, 4, 6]})

    result = score_correlations(frame, [("a_vs_b", "score_a", "score_b")])

    assert list(result.columns) == ["comparison", "pearson_r", "spearman_r", "n"]
    assert result.to_dict(orient="records") == [
        {"comparison": "a_vs_b", "pearson_r": 1.0, "spearman_r": 1.0, "n": 3}
    ]


def test_score_correlations_coerces_nonnumeric_values_and_drops_missing_pairs():
    frame = pd.DataFrame(
        {
            "score_a": ["1", "bad", "3", "", None],
            "score_b": ["2", "4", "6", "8", "10"],
        }
    )

    result = score_correlations(frame, [("coerced", "score_a", "score_b")])

    assert result.loc[0, "n"] == 2
    assert result.loc[0, "pearson_r"] == 1.0
    assert result.loc[0, "spearman_r"] == 1.0


def test_score_correlations_returns_missing_values_for_empty_frame():
    result = score_correlations(
        pd.DataFrame(columns=["score_a", "score_b"]),
        [("empty", "score_a", "score_b")],
    )

    assert result.loc[0, "comparison"] == "empty"
    assert result.loc[0, "n"] == 0
    assert_missing(result.loc[0, "pearson_r"])
    assert_missing(result.loc[0, "spearman_r"])


def test_score_correlations_returns_missing_values_for_missing_comparison_column():
    result = score_correlations(
        pd.DataFrame({"score_a": [1, 2, 3]}),
        [("missing_right", "score_a", "score_b")],
    )

    assert result.loc[0, "comparison"] == "missing_right"
    assert result.loc[0, "n"] == 0
    assert_missing(result.loc[0, "pearson_r"])
    assert_missing(result.loc[0, "spearman_r"])


def test_score_correlations_returns_missing_values_for_exactly_one_valid_pair():
    frame = pd.DataFrame({"score_a": [1, None], "score_b": [2, 4]})

    result = score_correlations(frame, [("one_pair", "score_a", "score_b")])

    assert result.loc[0, "n"] == 1
    assert_missing(result.loc[0, "pearson_r"])
    assert_missing(result.loc[0, "spearman_r"])


def test_score_correlations_constant_vector_has_undefined_correlations():
    frame = pd.DataFrame({"constant": [1, 1, 1], "score_b": [2, 3, 4]})

    result = score_correlations(frame, [("constant", "constant", "score_b")])

    assert result.loc[0, "n"] == 3
    assert_missing(result.loc[0, "pearson_r"])
    assert_missing(result.loc[0, "spearman_r"])


def gene_set_loads(
    left_valid=True,
    right_valid=True,
    left_up=None,
    right_up=None,
    left_down=None,
    right_down=None,
):
    return {
        "left": {
            "valid": left_valid,
            "status_message": None if left_valid else "left invalid",
            "UP": set() if left_up is None else set(left_up),
            "DOWN": set() if left_down is None else set(left_down),
        },
        "right": {
            "valid": right_valid,
            "status_message": None if right_valid else "right invalid",
            "UP": set() if right_up is None else set(right_up),
            "DOWN": set() if right_down is None else set(right_down),
        },
    }


def test_gene_set_overlap_row_reports_expected_keys_and_valid_up_overlap():
    row = gene_set_overlap_row(
        "dose",
        "left",
        "right",
        "UP",
        gene_set_loads(left_up={"A", "B", "C"}, right_up={"B", "C", "D", "E"}),
    )

    assert list(row) == [
        "comparison",
        "direction",
        "left_artifact",
        "right_artifact",
        "left_size",
        "right_size",
        "overlap_size",
        "retained_fraction_of_left",
        "retained_fraction_of_right",
        "status_message",
    ]
    assert row == {
        "comparison": "dose",
        "direction": "UP",
        "left_artifact": "left",
        "right_artifact": "right",
        "left_size": 3,
        "right_size": 4,
        "overlap_size": 2,
        "retained_fraction_of_left": 2 / 3,
        "retained_fraction_of_right": 2 / 4,
        "status_message": (
            "ok; retained_fraction_of_left uses overlap_size/left_size; "
            "retained_fraction_of_right uses overlap_size/right_size"
        ),
    }


def test_gene_set_overlap_row_reports_valid_down_overlap():
    row = gene_set_overlap_row(
        "dose",
        "left",
        "right",
        "DOWN",
        gene_set_loads(left_down={"A", "B"}, right_down={"B", "C"}),
    )

    assert row["left_size"] == 2
    assert row["right_size"] == 2
    assert row["overlap_size"] == 1
    assert row["retained_fraction_of_left"] == 1 / 2
    assert row["retained_fraction_of_right"] == 1 / 2


@pytest.mark.parametrize(
    ("left_valid", "right_valid", "expected_message"),
    [
        (False, True, "left invalid"),
        (True, False, "right invalid"),
        (False, False, "left invalid; right invalid"),
    ],
)
def test_gene_set_overlap_row_reports_invalid_artifacts(
    left_valid, right_valid, expected_message
):
    row = gene_set_overlap_row(
        "dose",
        "left",
        "right",
        "UP",
        gene_set_loads(left_valid=left_valid, right_valid=right_valid),
    )

    assert row["status_message"] == expected_message
    assert_missing(row["left_size"])
    assert_missing(row["right_size"])
    assert_missing(row["overlap_size"])
    assert_missing(row["retained_fraction_of_left"])
    assert_missing(row["retained_fraction_of_right"])


def test_gene_set_overlap_row_uses_missing_fraction_for_empty_left_denominator():
    row = gene_set_overlap_row(
        "dose",
        "left",
        "right",
        "UP",
        gene_set_loads(left_up=set(), right_up={"A", "B"}),
    )

    assert row["left_size"] == 0
    assert row["right_size"] == 2
    assert row["overlap_size"] == 0
    assert_missing(row["retained_fraction_of_left"])
    assert row["retained_fraction_of_right"] == 0


def test_gene_set_overlap_row_uses_missing_fraction_for_empty_right_denominator():
    row = gene_set_overlap_row(
        "dose",
        "left",
        "right",
        "UP",
        gene_set_loads(left_up={"A", "B"}, right_up=set()),
    )

    assert row["left_size"] == 2
    assert row["right_size"] == 0
    assert row["overlap_size"] == 0
    assert row["retained_fraction_of_left"] == 0
    assert_missing(row["retained_fraction_of_right"])


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
