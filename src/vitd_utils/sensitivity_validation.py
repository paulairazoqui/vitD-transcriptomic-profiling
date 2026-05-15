"""Read-only validation helpers for sensitivity robustness notebooks."""

import pandas as pd


def gene_set_overlap_row(comparison, left_artifact, right_artifact, direction, gene_set_pickle_loads):
    """Return one read-only gene-set overlap validation row.

    This validation helper expects preloaded gene-set pickle metadata in
    ``gene_set_pickle_loads`` and reads the already-loaded entries for
    ``left_artifact`` and ``right_artifact``. It does not load files, write
    files, or otherwise mutate notebook artifacts. When both artifacts are
    valid, retained fractions use explicit denominators: overlap divided by
    the left set size for ``retained_fraction_of_left`` and overlap divided by
    the right set size for ``retained_fraction_of_right``.
    """
    left_load = gene_set_pickle_loads[left_artifact]
    right_load = gene_set_pickle_loads[right_artifact]
    base_row = {
        "comparison": comparison,
        "direction": direction,
        "left_artifact": left_artifact,
        "right_artifact": right_artifact,
        "left_size": pd.NA,
        "right_size": pd.NA,
        "overlap_size": pd.NA,
        "retained_fraction_of_left": pd.NA,
        "retained_fraction_of_right": pd.NA,
        "status_message": None,
    }

    status_messages = []
    if not left_load["valid"]:
        status_messages.append(left_load["status_message"])
    if not right_load["valid"]:
        status_messages.append(right_load["status_message"])
    if status_messages:
        base_row["status_message"] = "; ".join(message for message in status_messages if message)
        return base_row

    left_set = left_load[direction]
    right_set = right_load[direction]
    overlap_size = len(left_set & right_set)
    left_size = len(left_set)
    right_size = len(right_set)

    base_row.update(
        {
            "left_size": left_size,
            "right_size": right_size,
            "overlap_size": overlap_size,
            "retained_fraction_of_left": overlap_size / left_size if left_size else pd.NA,
            "retained_fraction_of_right": overlap_size / right_size if right_size else pd.NA,
            "status_message": (
                "ok; retained_fraction_of_left uses overlap_size/left_size; "
                "retained_fraction_of_right uses overlap_size/right_size"
            ),
        }
    )
    return base_row


def score_correlations(frame, comparisons):
    """Return Pearson and Spearman score correlations for requested column pairs.

    Parameters
    ----------
    frame : pandas.DataFrame
        Table containing score columns to compare. Values in each requested
        pair are coerced with :func:`pandas.to_numeric` before rows with
        missing values are dropped.
    comparisons : iterable of tuple
        Ordered ``(comparison_label, left_column, right_column)`` tuples. One
        output row is returned for each tuple in the same order.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``comparison``, ``pearson_r``, ``spearman_r``,
        and ``n``. If the input frame is empty, a requested score column is
        missing, or fewer than two valid paired numeric rows remain, the
        corresponding correlation value is ``pd.NA``.
    """
    rows = []
    for comparison_label, left_column, right_column in comparisons:
        if frame.empty or left_column not in frame.columns or right_column not in frame.columns:
            rows.append(
                {
                    "comparison": comparison_label,
                    "pearson_r": pd.NA,
                    "spearman_r": pd.NA,
                    "n": 0,
                }
            )
            continue

        paired_scores = frame[[left_column, right_column]].apply(pd.to_numeric, errors="coerce").dropna()
        rows.append(
            {
                "comparison": comparison_label,
                "pearson_r": paired_scores[left_column].corr(paired_scores[right_column], method="pearson")
                if len(paired_scores) >= 2
                else pd.NA,
                "spearman_r": paired_scores[left_column].corr(paired_scores[right_column], method="spearman")
                if len(paired_scores) >= 2
                else pd.NA,
                "n": len(paired_scores),
            }
        )
    return pd.DataFrame(rows, columns=["comparison", "pearson_r", "spearman_r", "n"])


def path_label(path, project_root):
    """Return a repository-relative label for ``path`` when possible.

    ``None`` is preserved to match notebook display behavior. Paths that are
    outside ``project_root`` fall back to their string representation.
    """
    if path is None:
        return None
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def build_artifact_inventory(artifact_registry, project_root):
    """Build a read-only inventory table for registered sensitivity artifacts.

    This helper checks only whether each registered preferred and fallback path
    exists. It does not create, move, modify, or delete files. The returned
    DataFrame is suitable for notebook validation summaries and preserves the
    registry insertion order, path-selection behavior, boolean existence flags,
    and ``None`` path handling used by the sensitivity robustness notebook.
    """
    artifact_inventory_rows = []
    for artifact_name, metadata in artifact_registry.items():
        preferred_path = metadata["preferred_path"]
        fallback_path = metadata["fallback_path"]
        preferred_exists = preferred_path.exists() if preferred_path is not None else False
        fallback_exists = fallback_path.exists() if fallback_path is not None else False
        selected_path = preferred_path if preferred_exists else fallback_path if fallback_exists else preferred_path or fallback_path

        artifact_inventory_rows.append(
            {
                "artifact": artifact_name,
                "preferred_exists": preferred_exists,
                "fallback_exists": fallback_exists,
                "selected_path": path_label(selected_path, project_root),
                "artifact_type": metadata["artifact_type"],
                "status_role": metadata["status_role"],
            }
        )

    return pd.DataFrame(
        artifact_inventory_rows,
        columns=[
            "artifact",
            "preferred_exists",
            "fallback_exists",
            "selected_path",
            "artifact_type",
            "status_role",
        ],
    )


def resolve_registered_artifact(artifact_name, artifact_registry, project_root):
    """Resolve a registered artifact to the first existing preferred/fallback path.

    Returns ``(path, None)`` when an artifact path exists, otherwise returns
    ``(None, message)`` with the same diagnostic detail used by the notebook.
    """
    metadata = artifact_registry.get(artifact_name)
    if metadata is None:
        return None, f"{artifact_name}: not present in ARTIFACT_REGISTRY"

    candidates = [
        ("preferred", metadata.get("preferred_path")),
        ("fallback", metadata.get("fallback_path")),
    ]
    checked = []
    for label, path in candidates:
        exists = path.exists() if path is not None else False
        checked.append(f"{label}={path_label(path, project_root)} exists={exists}")
        if exists:
            return path, None

    return None, f"{artifact_name}: no readable artifact found ({'; '.join(checked)})"


def validation_detail(messages):
    """Format validation detail messages for a summary table row.

    Empty and ``None`` messages are omitted. If no messages remain, the
    standard no-issues message is returned.
    """
    cleaned = [str(message) for message in messages if message not in (None, "")]
    return "; ".join(cleaned) if cleaned else "No issues reported."


def missing_object_row(category, *object_names):
    """Build the standard failure row for missing in-memory validation objects."""
    return {
        "category": category,
        "status": "FAIL",
        "summary": "Expected validation output is not available in memory.",
        "detail": f"Run the earlier notebook section(s) that create: {', '.join(object_names)}.",
    }
