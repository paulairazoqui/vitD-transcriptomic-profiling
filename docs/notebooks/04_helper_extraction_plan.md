# Helper extraction plan

## 1. Purpose

This audit identifies notebook-local helper logic that can be extracted into `src` in a future pull request without changing scientific calculations, notebook behavior, or artifact locations in this PR. The immediate goal is documentation only: preserve all current notebooks and outputs while making the next extraction step explicit, reviewable, and testable.

Scope audited:

- `notebooks/04_directed_results.ipynb`
- `notebooks/04_directed_results_top30.ipynb`
- `notebooks/04_directed_results_plus3.ipynb`
- `notebooks/04_sensitivity_core_score_robustness.ipynb`

Important existing context:

- Consensus core-gene primitives already exist in `src/vitd_utils/coregenes.py`: `top_bottom_by_column`, `vote_counts`, `build_consensus_core`, and `core_score_for_matrix`.
- Preranked GSEA table construction already exists in `src/vitd_utils/gsea.py` as `make_preranked`.
- Several notebooks currently repeat orchestration around these primitives: parameter selection, score merging, result naming, artifact validation, overlap reporting, and safety policy checks.

## 2. Current duplication map

| Logic area | Current notebook locations | Current behavior | Duplication / reuse opportunity |
| --- | --- | --- | --- |
| Consensus core construction and scoring orchestration | `04_directed_results.ipynb` cell 12; `04_directed_results_top30.ipynb` cell 13; `04_directed_results_plus3.ipynb` cell 13 | Builds `effects_by_cell`, calls `coregenes.build_consensus_core(...)`, computes `core_score_for_matrix(...)`, drops any existing `META.core_score`, and merges scores back by `sig_id`. | Same orchestration repeated with different `top_n`, `min_votes`, `target_up`, and `target_dn` values. Existing `src` primitives are used correctly; extraction should wrap orchestration only. |
| Core-variant parameterization | Canonical notebook cell 12 uses `config.N_TOP`, `config.VOTE_MIN`, `config.CORE_UP_N`, `config.CORE_DN_N`; top30 notebook cell 13 hard-codes `top_n=30`; plus3 notebook cell 13 hard-codes `min_votes=3`, `target_up=18`, `target_dn=6`; sensitivity notebook cell 6 defines `VARIANTS`. | Parameters are spread across config, variant notebooks, and sensitivity registry. | A single dataclass or registry helper could make variant names and parameters auditable without altering calculations. |
| Vote/tie audit tables | `04_directed_results.ipynb` cell 16; `04_directed_results_top30.ipynb` cell 18; `04_directed_results_plus3.ipynb` cell 16 | Calls `top_bottom_by_column`, `vote_counts`, filters by `config.VOTE_MIN`, computes UP/DOWN tie scores, and creates `audit_up` / `audit_dn`. | Very similar logic, but top30 audit currently uses `top_n=100` despite a comment saying `# 50`; plus3 audit uses `config.VOTE_MIN` even though consensus scoring used `min_votes=3`. Extract only after clarifying whether those mismatches are intentional audit/provenance behavior. |
| Ranked gene lists for GSEA | `04_directed_results.ipynb` Section 6.1; `04_directed_results_top30.ipynb` cell 35; `04_directed_results_plus3.ipynb` cell 35 | Builds a symbol map from `geneinfo_beta.txt`, loops through `effects_by_cell.columns`, calls `gsea.make_preranked`, stores `{cell_id: DataFrame}`, optionally writes `.rnk` files under `config.RESULTS_DIR / "preranked_lists"`. | The loop and optional save policy are duplicated. `gsea.make_preranked` already handles one series; a future helper can handle a full matrix and safe optional writing. |
| Robustness score comparison | `04_directed_results.ipynb` cells 33-34; `04_sensitivity_core_score_robustness.ipynb` cells 13-17 | Canonical notebook manually reads top30/top50/top100 score CSVs and merges by `sig_id` for plotting. Sensitivity notebook resolves registered artifacts, validates loaders, merges score columns, and computes Pearson/Spearman globally and by cell line. | Sensitivity notebook has a more reusable validation implementation. Extraction is useful but should remain read-only and preserve the canonical plot code until equivalence is verified. |
| Sensitivity artifact validation | `04_sensitivity_core_score_robustness.ipynb` cells 2, 4, 6, 8, 9, 11, 13, 14, 26 | Defines project paths, source notebooks, `ARTIFACT_REGISTRY`, CSV schema checks, loader status tables, merge validation, and validation-summary rows. | Good candidate for extraction into validation utilities after separating pure path/registry helpers from notebook presentation. |
| Pickle gene-set validation and overlap validation | `04_sensitivity_core_score_robustness.ipynb` cells 4, 19, 20, 26 | Resolves registered pickle artifacts, loads read-only tuples of `(up_set, down_set)`, checks type/length/schema, computes overlap sizes and retained fractions for UP and DOWN. | Pure and reusable, but it touches historical/provenance artifacts and should wait until artifact naming and migration policy are confirmed. |
| Output path safety helpers | Variant notebook import cells: `04_directed_results_top30.ipynb` cell 3; `04_directed_results_plus3.ipynb` cell 3. Sensitivity notebook cells 2, 4, 6, 8, 9, 26. | Variant notebooks disable figure saving, redirect `config.RESULTS_DIR` and `config.FIG_DIR` to namespaced sensitivity subdirectories, and create directories. Sensitivity notebook labels paths relative to project root and summarizes output-safety policy. | A small path helper would reduce accidental manuscript-output overwrites, but mutating global `config` from a helper should be deferred or very carefully validated. |

## 3. Candidate helpers for src

### 3.1 `build_core_scores_table`

- **Proposed location/name:** `vitd_utils.coregenes.build_core_scores_table` or `vitd_utils.coreworkflow.build_core_scores_table`.
- **Current notebook locations:** `04_directed_results.ipynb` cell 12; `04_directed_results_top30.ipynb` cell 13; `04_directed_results_plus3.ipynb` cell 13.
- **Inputs:**
  - `exp: pd.DataFrame` genes × signatures expression/effect matrix.
  - `meta: pd.DataFrame` containing `sig_id` and cell metadata.
  - `top_n: int`.
  - `min_votes: int`.
  - `target_up: int`.
  - `target_dn: int`.
  - `min_non_na: int = 10`.
  - `center: bool = True`.
  - Optional `sig_id_col: str = "sig_id"`.
- **Outputs:** A structured result, preferably a small dataclass or dictionary containing:
  - `effects_by_cell`.
  - `consensus` from `coregenes.build_consensus_core`.
  - `core_up_ids` and `core_dn_ids`.
  - `core_scores` as a `pd.Series` indexed by `sig_id`.
  - `meta_with_core_score` with `core_score` merged by `sig_id`.
- **Safe now or should wait:** **Safe soon, but not in this PR.** The underlying calculation already lives in `src`; this helper would only centralize repeated orchestration.
- **Scientific risk level:** **Medium.** The risk is not mathematical novelty; it is accidental column-order, index, or merge behavior changes.
- **Required validation after extraction:**
  - Exact equality of `core_up_ids` and `core_dn_ids` for canonical, top30, and plus3 variants.
  - `pd.testing.assert_series_equal` for `core_scores`, including index names/order if relied upon.
  - `pd.testing.assert_frame_equal` for `META[["sig_id", "core_score"]]` after sorting by `sig_id`.
  - Confirm null counts and row counts match notebook output.

### 3.2 `CoreVariantSpec` / `get_core_variant_specs`

- **Proposed location/name:** `vitd_utils.coregenes.CoreVariantSpec` plus `vitd_utils.coregenes.get_core_variant_specs`, or a new `vitd_utils.sensitivity` module if broader sensitivity helpers are introduced.
- **Current notebook locations:** canonical cell 12, top30 cell 13, plus3 cell 13, sensitivity cell 6.
- **Inputs:** None for default registry; optionally a `config` object/module for project defaults.
- **Outputs:** Mapping from variant name to parameter record with fields `top_n`, `min_votes`, `target_up`, `target_dn`, and optional `label` / `artifact_suffix`.
- **Safe now or should wait:** **Safe soon, but not in this PR.** Best paired with `build_core_scores_table` so notebooks do not mix registry and ad hoc parameters.
- **Scientific risk level:** **Low to medium.** Low if values are copied verbatim; medium because variant labels can affect downstream artifact interpretation.
- **Required validation after extraction:**
  - Table-driven assertion that specs equal current notebook values: canonical `(50, 2, 42, 35)`, top30 `(30, 2, 42, 35)`, top100 `(100, 2, 42, 35)`, strict_plus3 `(50, 3, 18, 6)`.
  - Confirm variant notebooks still write/read the same artifact names if they adopt the registry later.

### 3.3 `consensus_vote_audit_tables`

- **Proposed location/name:** `vitd_utils.coregenes.consensus_vote_audit_tables`.
- **Current notebook locations:** `04_directed_results.ipynb` cell 16; `04_directed_results_top30.ipynb` cell 18; `04_directed_results_plus3.ipynb` cell 16.
- **Inputs:**
  - `effects_by_cell: pd.DataFrame`.
  - `top_n: int`.
  - `min_votes: int`.
  - `min_non_na: int = 10`.
- **Outputs:** Dictionary or dataclass containing `extremes`, `votes_up`, `votes_dn`, `up_ge_min`, `dn_ge_min`, `audit_up`, `audit_dn`.
- **Safe now or should wait:** **Should wait.** Current variant audit cells may not use the same parameters as their consensus cells.
- **Scientific risk level:** **High until clarified.** The top30 audit uses `top_n=100`; plus3 audit filters with `config.VOTE_MIN` rather than `3`. These may be intentional historical checks, but extraction could falsely standardize them.
- **Required validation after extraction:**
  - Preserve the exact `top_n` and `min_votes` values used by each audit cell, even where they differ from scoring parameters.
  - Exact equality for vote distributions, `audit_up`, and `audit_dn` ordering.
  - Notebook text/comments should be updated in the extraction PR only if scientific owners confirm the intended audit parameters.

### 3.4 `make_preranked_lists_by_column`

- **Proposed location/name:** `vitd_utils.gsea.make_preranked_lists_by_column`.
- **Current notebook locations:** Section 6.1 in `04_directed_results.ipynb`; `04_directed_results_top30.ipynb` cell 35; `04_directed_results_plus3.ipynb` cell 35.
- **Inputs:**
  - `effects_by_column: pd.DataFrame` genes × cell/context.
  - `sym_map: pd.Series`.
  - Optional `dropna: bool = True`.
- **Outputs:** `{column_name: preranked_df}` where each frame matches `gsea.make_preranked` output columns `gene` and `score`.
- **Safe now or should wait:** **Safe first extraction candidate.** It is a thin loop around an existing pure helper.
- **Scientific risk level:** **Low.** No change in ranking algorithm if it delegates directly to `make_preranked`.
- **Required validation after extraction:**
  - For every cell line, `pd.testing.assert_frame_equal` against current `ranked_lists[cell]`.
  - Confirm ordering, duplicate-symbol handling, and score values are unchanged.

### 3.5 `write_preranked_lists`

- **Proposed location/name:** `vitd_utils.gsea.write_preranked_lists` or `vitd_utils.io.write_preranked_lists`.
- **Current notebook locations:** same Section 6.1 / cell 35 blocks in all directed notebooks.
- **Inputs:**
  - `ranked_lists: Mapping[str, pd.DataFrame]`.
  - `out_dir: Path`.
  - Optional `prefix: str = "preranked"`.
  - Optional `enabled: bool` to mirror `config.SAVE_TABLES`.
- **Outputs:** List of written `Path` objects; no writes when disabled.
- **Safe now or should wait:** **Safe after path policy is reviewed.** Writing behavior is optional but path construction must remain exactly namespaced.
- **Scientific risk level:** **Low.** Risk is operational rather than scientific.
- **Required validation after extraction:**
  - With writes disabled, assert no filesystem changes.
  - With writes enabled in a temporary directory, compare exact file names and tab-delimited no-header content.

### 3.6 `score_correlations`

- **Proposed location/name:** `vitd_utils.sensitivity.score_correlations` or `vitd_utils.stats.score_correlations`.
- **Current notebook locations:** `_score_correlations` in `04_sensitivity_core_score_robustness.ipynb` cell 4; used in cells 15 and 17.
- **Inputs:**
  - `frame: pd.DataFrame`.
  - `comparisons: Sequence[tuple[str, str, str]]` as `(label, left_column, right_column)`.
- **Outputs:** `pd.DataFrame` with columns `comparison`, `pearson_r`, `spearman_r`, `n`.
- **Safe now or should wait:** **Safe first extraction candidate.** Pure, deterministic, read-only.
- **Scientific risk level:** **Low.** It summarizes already-produced scores; it does not create scores.
- **Required validation after extraction:**
  - Exact equality of `global_robustness_correlations` and `per_cell_robustness_correlations`.
  - Explicit tests for missing columns, empty frames, numeric coercion, and `n < 2` behavior.

### 3.7 `merge_robustness_score_tables`

- **Proposed location/name:** `vitd_utils.sensitivity.merge_robustness_score_tables`.
- **Current notebook locations:** `04_directed_results.ipynb` cell 33; `04_sensitivity_core_score_robustness.ipynb` cells 13-14 and 17.
- **Inputs:**
  - Mapping from artifact name or label to loaded score table.
  - Mapping from artifact name to output score column, e.g. `score30`, `score50`, `score100`.
  - Optional required columns, default `{"sig_id", "core_score"}`.
  - Optional `include_cell_id: bool` for per-cell checks.
- **Outputs:**
  - Merged score frame by `sig_id`.
  - Validation/status frame with missing columns, duplicate IDs, missing score counts, and messages.
- **Safe now or should wait:** **Should wait until after `score_correlations`.** Merge semantics determine which signatures are compared and therefore need careful equivalence testing.
- **Scientific risk level:** **Medium.** Inner joins, duplicate `sig_id`, and cell-line consistency filters can alter `n` and correlations.
- **Required validation after extraction:**
  - Exact merged row counts and missing-score counts.
  - Exact `sig_id` membership for global and per-cell merged frames.
  - Match canonical scatter input table used in robustness plots.
  - Preserve behavior when any artifact is unavailable.

### 3.8 `path_label` and `resolve_registered_artifact`

- **Proposed location/name:** `vitd_utils.sensitivity.path_label` and `vitd_utils.sensitivity.resolve_registered_artifact`.
- **Current notebook locations:** `_path_label` and `_resolve_registered_artifact` in `04_sensitivity_core_score_robustness.ipynb` cell 4; used throughout cells 9, 11, 13, 19, and 26.
- **Inputs:**
  - `path: Path | None` and `project_root: Path` for `path_label`.
  - `artifact_name: str`, `artifact_registry: Mapping`, and `project_root: Path` for `resolve_registered_artifact`.
- **Outputs:**
  - Relative or absolute string label for paths.
  - `(selected_path, warning)` for artifact resolution.
- **Safe now or should wait:** **Safe first extraction candidate** if implemented as pure functions that receive registry/root explicitly.
- **Scientific risk level:** **Low.** These functions do not compute biological results.
- **Required validation after extraction:**
  - Exact `artifact_inventory.selected_path` strings.
  - Exact loader warning messages for missing artifacts.
  - Tests for `None`, in-root, and out-of-root paths.

### 3.9 `validate_csv_artifacts`

- **Proposed location/name:** `vitd_utils.sensitivity.validate_csv_artifacts`.
- **Current notebook locations:** `04_sensitivity_core_score_robustness.ipynb` cell 11.
- **Inputs:**
  - `artifact_registry`.
  - `expected_columns: set[str]`.
  - Optional path resolver.
- **Outputs:** `pd.DataFrame` with artifact name, existence, selected path, row count, column count, missing expected columns, and read error.
- **Safe now or should wait:** **Safe after path helpers.** It reads artifacts but does not write or transform results.
- **Scientific risk level:** **Low.** Validation-only.
- **Required validation after extraction:**
  - Exact equality of `csv_schema_validation`.
  - Tests for missing file, malformed file, missing required column, and valid CSV.

### 3.10 `load_gene_set_pickle` and `gene_set_overlap_row`

- **Proposed location/name:** `vitd_utils.sensitivity.load_gene_set_pickle` and `vitd_utils.sensitivity.gene_set_overlap_row`.
- **Current notebook locations:** `_load_registered_gene_set_pickle` and `_gene_set_overlap_row` in `04_sensitivity_core_score_robustness.ipynb` cell 4; used in cells 19 and 20.
- **Inputs:**
  - Artifact name and registry/path resolver for loading.
  - Loaded left/right records and direction (`"up"` or `"down"`) for overlap.
- **Outputs:**
  - Load-result dictionary with `available`, `valid`, `up`, `down`, and `status_message`.
  - Overlap row with sizes, overlap count, retained fractions, and status message.
- **Safe now or should wait:** **Should wait.** The current logic references historical notebook-root pickle names and contains provenance-specific messaging.
- **Scientific risk level:** **Medium.** Overlap summaries are validation-only, but loading the wrong artifact could misrepresent sensitivity conclusions.
- **Required validation after extraction:**
  - Exact equality of `gene_set_pickle_validation` and `gene_set_overlap_validation`.
  - Tests for non-tuple pickle, tuple of wrong length, non-set members, missing artifact, empty sets, and valid sets.
  - Confirm artifact paths are intentionally historical or migrated before changing registry defaults.

### 3.11 `configure_variant_output_dirs`

- **Proposed location/name:** `vitd_utils.config.configure_variant_output_dirs` or `vitd_utils.paths.configure_variant_output_dirs`.
- **Current notebook locations:** `04_directed_results_top30.ipynb` cell 3; `04_directed_results_plus3.ipynb` cell 3.
- **Inputs:**
  - `variant_name: str`.
  - `root_dir: Path` or config module.
  - Optional `save_figs: bool = False`.
  - Optional `create: bool = True`.
- **Outputs:** Variant result and figure directories; optionally updated config values if mutation is explicitly requested.
- **Safe now or should wait:** **Should wait.** Current code mutates global `config.RESULTS_DIR`, `config.FIG_DIR`, and `config.SAVE_FIGS`; hiding this behind a helper could make side effects less visible.
- **Scientific risk level:** **Medium operational risk.** The scientific calculations are unchanged, but artifact overwrites or misplaced outputs are high-impact project risks.
- **Required validation after extraction:**
  - Dry-run mode test with no directory creation.
  - With creation enabled, paths exactly match `results/sensitivity/top30` and `results/sensitivity/plus3`.
  - Verify `config.SAVE_FIGS` remains `False` in variant notebooks and canonical manuscript output dirs are untouched.

### 3.12 `summarize_validation_status`

- **Proposed location/name:** `vitd_utils.sensitivity.summarize_validation_status`.
- **Current notebook locations:** `04_sensitivity_core_score_robustness.ipynb` cell 26.
- **Inputs:** Named validation objects or a dictionary containing artifact status, inventory, CSV validation, loader status, merge validation, correlations, pickle validation, overlap validation, and output policy.
- **Outputs:** `pd.DataFrame` with columns `category`, `status`, `summary`, `detail`.
- **Safe now or should wait:** **Should wait until lower-level validators are extracted.** The summary is presentation/orchestration around multiple notebook globals.
- **Scientific risk level:** **Low to medium.** Validation-only, but summary status labels drive review attention.
- **Required validation after extraction:**
  - Exact equality of `validation_summary`.
  - Tests for missing objects, warnings, failures, and pass cases.

## 4. Safe first extraction candidates

Recommended low-risk helpers for the first code-extraction PR after this documentation PR:

1. **`gsea.make_preranked_lists_by_column`**
   - Thin loop around the existing `gsea.make_preranked` implementation.
   - No file writes, no core-score changes, and no artifact-path changes.

2. **`sensitivity.score_correlations`**
   - Pure function currently defined as `_score_correlations`.
   - Deterministic summary of already-computed score columns.

3. **`sensitivity.path_label`**
   - Pure path formatting helper.
   - Useful prerequisite for artifact validators.

4. **`sensitivity.resolve_registered_artifact`**
   - Safe if it remains explicit about the registry and root passed in.
   - Should not embed project-specific artifact names in the function body.

5. **`sensitivity.validate_csv_artifacts`**
   - Safe after path resolution is extracted.
   - Read-only and validation-only.

6. **`coregenes.build_core_scores_table`**
   - Safe as a second small extraction once tests prove exact equivalence across canonical, top30, and plus3 variants.
   - This is the most valuable orchestration helper, but it directly affects manuscript-level score columns, so it should not be first unless equivalence checks are already automated.

## 5. Deferred/high-risk candidates

Defer these until ambiguity and artifact policy are resolved:

1. **`consensus_vote_audit_tables`**
   - Reason: current audit parameter choices differ from scoring parameters in variant notebooks.
   - Needed decision: should audit cells use variant-specific parameters or preserve historical hard-coded/config-derived checks?

2. **`merge_robustness_score_tables`**
   - Reason: join type and duplicate handling define comparison populations.
   - Needed decision: should canonical robustness plotting and sensitivity validation share one merge implementation immediately, or should the sensitivity notebook migrate first?

3. **`load_gene_set_pickle` / `gene_set_overlap_row`**
   - Reason: current registry uses historical/provenance pickle paths and status messaging.
   - Needed decision: whether to keep historical notebook-root artifacts, migrate to namespaced sensitivity artifacts, or support both explicitly.

4. **`configure_variant_output_dirs`**
   - Reason: global config mutation controls output safety.
   - Needed decision: whether helper should mutate `config` or return directories for explicit assignment in notebooks.

5. **`summarize_validation_status`**
   - Reason: depends on several lower-level validators and notebook-global object names.
   - Needed decision: stabilize validator output schemas first.

## 6. Required equivalence checks

Future extraction PRs should include these checks before notebook code is switched to call `src` helpers:

### Core-score equivalence

- Re-run the canonical, top30, and plus3 score-building cells before and after extraction.
- Assert identical core gene IDs by direction and variant.
- Assert identical `core_score` values by `sig_id`.
- Assert identical `META` row count, `sig_id` membership, and `core_score` null count.
- Confirm canonical `core_scores_top50.csv` and variant score CSVs are not rewritten unless intentionally requested.

### Ranked-list equivalence

- For each cell line, compare the full preranked DataFrame from the helper to the current notebook loop output.
- Check gene-symbol fallback behavior for unmapped IDs.
- Check duplicate-symbol resolution by largest absolute score.
- If write helper is introduced, write to a temporary directory and compare exact `.rnk` bytes or parsed tabular content.

### Variant-parameter equivalence

- Assert variant registry values match current notebooks:
  - canonical_top50: `top_n=50`, `min_votes=2`, `target_up=42`, `target_dn=35`.
  - top30: `top_n=30`, `min_votes=2`, `target_up=42`, `target_dn=35`.
  - top100: `top_n=100`, `min_votes=2`, `target_up=42`, `target_dn=35`.
  - strict_plus3: `top_n=50`, `min_votes=3`, `target_up=18`, `target_dn=6`.
- Separately assert audit-cell parameters if `consensus_vote_audit_tables` is extracted, because audit parameters are not fully aligned with scoring parameters today.

### Robustness and sensitivity equivalence

- Assert exact equality of:
  - `artifact_inventory`.
  - `csv_schema_validation`.
  - `robustness_loader_status`.
  - `robustness_merge_validation`.
  - `global_robustness_correlations`.
  - `per_cell_robustness_status`.
  - `per_cell_robustness_correlations`.
  - `gene_set_pickle_validation`.
  - `gene_set_overlap_validation`.
  - `validation_summary`.
- Compare merged robustness score `sig_id` sets, row counts, and correlation `n` values before comparing coefficients.
- Validate behavior when one or more sensitivity artifacts are absent, because the notebook currently supports historical fallbacks.

### Output safety equivalence

- Confirm no canonical manuscript output directory is changed by variant helpers.
- Confirm variant notebooks still point to:
  - `results/sensitivity/top30` for top30.
  - `results/sensitivity/plus3` for plus3.
- Confirm `config.SAVE_FIGS = False` remains visible and effective for variant notebooks.
- Confirm validation-only sensitivity helpers do not write files, regenerate artifacts, or create figures.

## 7. Recommended PR sequence

1. **PR 1: Documentation/audit only**
   - Add this plan.
   - Do not modify notebooks, `src`, data, results, figures, or README.

2. **PR 2: Pure low-risk helpers with tests**
   - Add `make_preranked_lists_by_column`.
   - Add `score_correlations`, `path_label`, and `resolve_registered_artifact` in a sensitivity-oriented module.
   - Add unit tests using small in-memory DataFrames and temporary paths.
   - Do not change notebooks yet unless tests demonstrate exact replacement output.

3. **PR 3: Validation helper extraction**
   - Add `validate_csv_artifacts` and possibly artifact inventory construction.
   - Keep notebook behavior read-only and validation-only.
   - Compare sensitivity notebook validation tables exactly.

4. **PR 4: Core-score orchestration helper**
   - Add `CoreVariantSpec` and `build_core_scores_table`.
   - Add equivalence tests for canonical, top30, and plus3 parameter sets.
   - Migrate one notebook at a time only after exact score equivalence is proven.

5. **PR 5: Robustness merge and overlap helpers**
   - Add robustness merge utilities after join semantics are approved.
   - Add pickle-load and gene-set-overlap utilities only after deciding whether historical artifact paths remain supported.

6. **PR 6: Optional output path helper**
   - Add a clearly named helper for variant output directories.
   - Prefer returning directories over hidden global mutation unless notebooks intentionally assign config values in visible lines.
