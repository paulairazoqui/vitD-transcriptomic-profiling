"""Read-only validation helpers for sensitivity robustness notebooks."""


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
