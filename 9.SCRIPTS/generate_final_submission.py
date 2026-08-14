"""Build the clean Round-4 evidence snapshot and artifact-driven final report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

import nbformat
import pandas as pd

from submission_sanitizer import (
    TEXT_EXTENSIONS,
    current_python_path,
    empty_replacement_counts,
    sanitize_public_file,
    scan_public_tree,
)


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = (ROOT / "FINAL_SUBMISSION").resolve()
FE_DIR = ROOT / "7.ML" / "7.6.feature_engineering"
EVAL_DIR = ROOT / "4.MODELS" / "4.2.evaluation"
MODEL_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
SECONDARY_DIR = ROOT / "4.MODELS" / "hitradar_secondary"
VALIDATION_DIR = ROOT / "5.UNG_DUNG" / "validation"
LEGACY_PREFIXES = ("HOTFIX_", "OUTPUT_", "BEFORE_", "BACKUP_")
HISTORICAL_CAVEAT = (
    "The 2019+ horizon was not used for corrected Round-2 winner selection, "
    "but had been inspected during an earlier development iteration."
)
CANONICAL_COMMANDS = (
    r"py -3.12 -m venv .venv_round4",
    r".\.venv_round4\Scripts\python -m pip install --upgrade pip",
    r".\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt",
    r'.\.venv_round4\Scripts\python -m ipykernel install --user --name hitradar-round4 --display-name "HitRadar Round4 Validation"',
    r'$env:HITRADAR_KERNEL_NAME="hitradar-round4"',
    r".\.venv_round4\Scripts\python .\9.SCRIPTS\generate_temporal_year_coverage.py",
    r'.\.venv_round4\Scripts\python .\scratch\build_notebooks_05_07.py --only "05,07"',
    r".\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.5.feature_engineering\05_feature_engineering.ipynb",
    r".\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.7.demo\07_ai_deployment.ipynb",
    r".\.venv_round4\Scripts\python .\9.SCRIPTS\record_round4_notebook_status.py",
    r".\.venv_round4\Scripts\python .\9.SCRIPTS\run_round4_tests.py",
    r".\.venv_round4\Scripts\python .\9.SCRIPTS\generate_final_submission.py --final",
)
PRIVATE_RAW_BASELINE_SHA256 = {
    "5.UNG_DUNG/validation/round4_environment_install.log": "923d30064c4baba01377075dd3cc6e10f3834dbaa8dc664a2026521ca0512df2",
    "5.UNG_DUNG/validation/round4_environment_validation.json": "c925b44f1b199e64541eff939b2690e85c3e10bf90fd3eaa5e003ef835336163",
    "5.UNG_DUNG/validation/round4_notebook_execution_status.json": "2c9a45ec67683d2f387c5c06ce101647ce4d8c2f437f8701cc1480c93c5529f0",
    "5.UNG_DUNG/validation/round4_test_results.json": "161a88396c74a74a47cc85bf7c9916313f5575fba2540662f1da3ecb4f4b7ba9",
}
PRIVATE_RAW_ROOT = ROOT / "scratch" / "private_evidence" / "pre_repository_sanitization"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    checksum = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def assert_clean_generated_markdown(text: str, expected: tuple[str, ...] = ()) -> None:
    forbidden = [character for character in text if ord(character) < 32 and character not in "\n\r\t"]
    if forbidden:
        raise AssertionError(f"Generated markdown contains control characters: {[ord(c) for c in forbidden]}")
    missing = [literal for literal in expected if literal not in text]
    if missing:
        raise AssertionError(f"Generated markdown is missing literal commands: {missing}")


def markdown_table(frame: pd.DataFrame, digits: int = 6) -> str:
    view = frame.copy()
    for column in view.select_dtypes(include="number").columns:
        view[column] = view[column].map(
            lambda value: f"{value:.{digits}f}" if pd.notna(value) else ""
        )
    headers = [str(column) for column in view.columns]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in view.astype(str).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def snapshot_hashes(relative_paths: tuple[str, ...] | list[str]) -> dict[str, str]:
    return {relative: digest(ROOT / relative) for relative in relative_paths}


def sanitize_submission_copies(python_executable: Path) -> tuple[dict[str, int], list[dict]]:
    totals = empty_replacement_counts()
    sanitized_files: list[dict] = []
    audited_root = python_executable.resolve().parents[2]
    project_roots = list(dict.fromkeys([audited_root, ROOT.resolve()]))
    for path in sorted(SUBMISSION.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        file_counts = empty_replacement_counts()
        for project_root in project_roots:
            counts = sanitize_public_file(
                path,
                project_root=project_root,
                user_home=Path.home(),
                python_executable=python_executable,
            )
            for category, count in counts.items():
                file_counts[category] += count
                totals[category] += count
        if sum(file_counts.values()):
            sanitized_files.append({
                "file": path.relative_to(SUBMISSION).as_posix(),
                "replacement_counts": {key: value for key, value in file_counts.items() if value},
            })
    return totals, sanitized_files


def safe_reset_submission() -> None:
    expected = (ROOT.resolve() / "FINAL_SUBMISSION")
    if SUBMISSION != expected or SUBMISSION.name != "FINAL_SUBMISSION":
        raise RuntimeError(f"Unsafe submission target: {SUBMISSION}")
    if SUBMISSION.exists():
        shutil.rmtree(SUBMISSION)
    for directory in ["notebooks", "src", "deployment", "evidence", "tests", "scripts"]:
        (SUBMISSION / directory).mkdir(parents=True, exist_ok=True)


COPY_MAP = {
    "3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb": "notebooks/05_feature_engineering.ipynb",
    "3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb": "notebooks/06_machine_learning.ipynb",
    "3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb": "notebooks/07_ai_deployment.ipynb",
    "src/features.py": "src/features.py",
    "src/evaluation.py": "src/evaluation.py",
    "src/modeling.py": "src/modeling.py",
    "src/secondary_tasks.py": "src/secondary_tasks.py",
    "src/prediction_policy.py": "src/prediction_policy.py",
    "5.UNG_DUNG/5.1.backend_api/api.py": "deployment/api.py",
    "5.UNG_DUNG/5.1.backend_api/models/prediction.py": "deployment/prediction.py",
    "5.UNG_DUNG/5.2.frontend/streamlit_app.py": "deployment/streamlit_app.py",
    "5.UNG_DUNG/5.3.config/requirements.txt": "deployment/requirements.txt",
    "5.UNG_DUNG/5.3.config/RUNTIME_ENVIRONMENT.md": "deployment/RUNTIME_ENVIRONMENT.md",
    "7.ML/7.6.feature_engineering/feature_contract.json": "evidence/feature_contract.json",
    "7.ML/7.6.feature_engineering/candidate_feature_evaluation.csv": "evidence/candidate_feature_evaluation.csv",
    "7.ML/7.6.feature_engineering/feature_dependency_leakage_audit.csv": "evidence/feature_dependency_leakage_audit.csv",
    "7.ML/7.6.feature_engineering/feature_validation.csv": "evidence/feature_validation.csv",
    "7.ML/7.6.feature_engineering/train_stat_immutability.json": "evidence/train_stat_immutability.json",
    "4.MODELS/4.2.evaluation/model_selection_validation_metrics.csv": "evidence/model_selection_validation_metrics.csv",
    "4.MODELS/hitradar_popularity/selection_winner_lock.json": "evidence/selection_winner_lock.json",
    "4.MODELS/hitradar_popularity/final_test_metrics.json": "evidence/final_test_metrics.json",
    "4.MODELS/4.2.evaluation/validation_time_bias_comparison.csv": "evidence/validation_time_bias_comparison.csv",
    "4.MODELS/4.2.evaluation/final_error_groups.csv": "evidence/final_error_groups.csv",
    "4.MODELS/4.2.evaluation/final_grouped_feature_importance.csv": "evidence/final_grouped_feature_importance.csv",
    "4.MODELS/hitradar_secondary/cluster_metadata.json": "evidence/cluster_metadata.json",
    "4.MODELS/hitradar_secondary/kmeans_k_selection.csv": "evidence/kmeans_k_selection.csv",
    "4.MODELS/hitradar_secondary/recommendation_metadata.json": "evidence/recommendation_metadata.json",
    "4.MODELS/hitradar_secondary/recommendation_examples.csv": "evidence/recommendation_examples.csv",
    "5.UNG_DUNG/validation/temporal_year_coverage.json": "evidence/temporal_year_coverage.json",
    "5.UNG_DUNG/validation/round4_environment_validation.json": "evidence/round4_environment_validation.json",
    "5.UNG_DUNG/validation/round4_environment_install.log": "evidence/round4_environment_install.log",
    "5.UNG_DUNG/validation/round4_notebook_execution_status.json": "evidence/round4_notebook_execution_status.json",
    "5.UNG_DUNG/validation/round4_end_to_end_validation.json": "evidence/round4_end_to_end_validation.json",
    "5.UNG_DUNG/validation/round4_test_results.json": "evidence/round4_test_results.json",
    "5.UNG_DUNG/validation/round4_model_integrity.json": "evidence/round4_model_integrity.json",
    "5.UNG_DUNG/validation/shap_requirement_status.json": "evidence/shap_requirement_status.json",
    "5.UNG_DUNG/validation/public_path_hotfix_test_results.json": "evidence/public_path_hotfix_test_results.json",
    "tests/test_feature_pipeline.py": "tests/test_feature_pipeline.py",
    "9.SCRIPTS/run_round4_tests.py": "scripts/run_round4_tests.py",
    "9.SCRIPTS/generate_temporal_year_coverage.py": "scripts/generate_temporal_year_coverage.py",
    "9.SCRIPTS/validate_round4_environment.py": "scripts/validate_round4_environment.py",
    "9.SCRIPTS/record_round4_notebook_status.py": "scripts/record_round4_notebook_status.py",
    "9.SCRIPTS/validate_round4_model_integrity.py": "scripts/validate_round4_model_integrity.py",
    "9.SCRIPTS/run_public_path_hotfix_tests.py": "scripts/run_public_path_hotfix_tests.py",
    "9.SCRIPTS/generate_final_submission.py": "scripts/generate_final_submission.py",
}


def collect_git_evidence() -> str:
    if not (ROOT / ".git").exists():
        return (
            "# Git Evidence\n\nGit metadata was not present in this working copy. Git history, "
            "branches, commits and pull-request evidence cannot be verified from this workspace.\n\n"
            "No `git init`, fabricated commit, branch, reviewer, or pull-request record was created.\n"
        )
    commands = [
        ["git", "status", "--short"], ["git", "branch", "--show-current"],
        ["git", "log", "--oneline", "--decorate", "-n", "20"],
        ["git", "branch", "--list"], ["git", "remote", "-v"],
        ["git", "diff", "--stat"],
        ["git", "diff", "--name-status"],
        ["git", "diff", "--cached", "--stat"],
        ["git", "diff", "--cached", "--name-status"],
    ]
    sections = ["# Git Evidence", "", "All output below was collected from the actual working tree."]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        raw_output = completed.stdout or completed.stderr or "(no output)"
        output = "\n".join(line.rstrip() for line in raw_output.splitlines())
        sections += ["", f"## `{' '.join(command)}`", "", "```text", output, "```"]
    return "\n".join(sections) + "\n"


def write_readme(final_metrics: dict, coverage: dict, integrity: dict, shap: dict) -> str:
    commands = "\n".join(CANONICAL_COMMANDS)
    late_year_rows = {
        year: rows for year, rows in coverage["rows_by_year"].items()
        if int(year) >= coverage["final_temporal_holdout"]["min_year"]
    }
    readme = rf"""# HitRadar — Final Submission

> **Package semantics:** `FINAL_SUBMISSION` is a clean submission/evidence snapshot. Full notebook execution and deployment require the canonical HitRadar repository plus the external artifacts/data listed in `evidence/external_artifact_checksums.json`. This snapshot is **not standalone runnable**.

## Project scope

Main task: Spotify popularity regression. Secondary tasks: audio clustering and content-based recommendation.

## Temporal governance and support

- Selection train: `release_year <= 2017`; validation: 2018.
- Final refit: `release_year < 2019`; final temporal holdout: `release_year >= 2019`.
- Training ends in 2018. Observed data spans {coverage['min_release_year']}–{coverage['max_release_year']}.
- Final holdout spans {coverage['final_temporal_holdout']['min_year']}–{coverage['final_temporal_holdout']['max_year']} with {coverage['final_temporal_holdout']['rows']:,} rows.
- HitRadar intentionally uses {coverage['product_support_end_year']} as a conservative **product-support cutoff**. Observed rows after that year do not extend a production support guarantee.
- Late-year row evidence is loaded from `temporal_year_coverage.json`: `{json.dumps(late_year_rows, ensure_ascii=False)}`.

{HISTORICAL_CAVEAT} This preserves lock-before-evaluation evidence without a project-wide “never observed” claim.

## Current evidence and limitations

- Locked winner: **{final_metrics['selection_winner_experiment']} / {final_metrics['selection_winner_model']}**.
- Clipped final metrics: MAE **{final_metrics['clipped_test_metrics']['MAE']:.6f}**, RMSE **{final_metrics['clipped_test_metrics']['RMSE']:.6f}**, R² **{final_metrics['clipped_test_metrics']['R2']:.6f}**.
- Notebook 06 was not retrained in Round 4; model checksum unchanged: **{integrity['production_model']['unchanged']}**.
- Performance remains modest, the high-popularity tail is difficult, and time variables are influential.
- KMeans separation is modest; recommendation has no human relevance study or fabricated artist/title metadata.
- Git evidence is **{'verifiable' if (ROOT / '.git').exists() else 'not verifiable in this workspace'}**.
- SHAP status: **{shap['decision']}**; it was not added because the inspected checklist labels it as an advanced, not mandatory, item.

## A. Run from the canonical repository root

These commands require the full repository, canonical `4.MODELS/` and `5.DATA/` artifacts. Notebook 06 is intentionally omitted because Round 4 does not change production model inputs or behavior.

```powershell
{commands}
```

## B. Inspect the FINAL_SUBMISSION snapshot

- `notebooks/`: canonical notebook snapshots (Notebook 06 is preserved, not retrained in Round 4).
- `src/`: shared-source snapshot.
- `deployment/`: API/schema/UI snapshot and the single current requirements file.
- `evidence/`: feature, model, environment, temporal coverage, tests, checksums, and execution evidence.
- `tests/` and `scripts/`: current verification source.
- Large model and parquet artifacts are not duplicated. Use their canonical paths and SHA-256 values in `evidence/external_artifact_checksums.json`.

## Evidence path sanitization

Machine-specific absolute paths and local usernames are sanitized in the tracked repository and this public snapshot. Pre-sanitization raw copies are retained only under ignored `scratch/private_evidence/` for local audit and are not part of the public repository. The public report records both private-original and tracked-sanitized checksums without publishing private paths.
"""
    assert_clean_generated_markdown(readme, CANONICAL_COMMANDS)
    (SUBMISSION / "README_FINAL_SUBMISSION.md").write_text(readme, encoding="utf-8")
    return readme


def main(final_mode: bool) -> None:
    private_raw_hashes = {
        relative: digest(PRIVATE_RAW_ROOT / relative)
        for relative in PRIVATE_RAW_BASELINE_SHA256
    }
    if private_raw_hashes != PRIVATE_RAW_BASELINE_SHA256:
        changed = [
            relative for relative, checksum in private_raw_hashes.items()
            if checksum != PRIVATE_RAW_BASELINE_SHA256[relative]
        ]
        raise AssertionError(f"Private raw Round-4 evidence is missing or changed: {changed}")
    tracked_sanitized_before = snapshot_hashes(tuple(PRIVATE_RAW_BASELINE_SHA256))
    model_path = MODEL_DIR / "popularity_pipeline.joblib"
    metrics_path = MODEL_DIR / "final_test_metrics.json"
    model_sha_before = digest(model_path)
    metrics_sha_before = digest(metrics_path)

    contract = load_json(FE_DIR / "feature_contract.json")
    candidate = pd.read_csv(FE_DIR / "candidate_feature_evaluation.csv")
    leakage = pd.read_csv(FE_DIR / "feature_dependency_leakage_audit.csv")
    feature_validation = pd.read_csv(FE_DIR / "feature_validation.csv")
    immutability = load_json(FE_DIR / "train_stat_immutability.json")
    selection = pd.read_csv(EVAL_DIR / "model_selection_validation_metrics.csv")
    lock = load_json(MODEL_DIR / "selection_winner_lock.json")
    final_metrics = load_json(MODEL_DIR / "final_test_metrics.json")
    time_bias = pd.read_csv(EVAL_DIR / "validation_time_bias_comparison.csv")
    error_groups = pd.read_csv(EVAL_DIR / "final_error_groups.csv")
    importance = pd.read_csv(EVAL_DIR / "final_grouped_feature_importance.csv")
    k_scores = pd.read_csv(SECONDARY_DIR / "kmeans_k_selection.csv")
    cluster = load_json(SECONDARY_DIR / "cluster_metadata.json")
    recommendation = load_json(SECONDARY_DIR / "recommendation_metadata.json")
    coverage = load_json(VALIDATION_DIR / "temporal_year_coverage.json")
    environment = load_json(VALIDATION_DIR / "round4_environment_validation.json")
    notebook_status = load_json(VALIDATION_DIR / "round4_notebook_execution_status.json")
    e2e = load_json(VALIDATION_DIR / "round4_end_to_end_validation.json")
    integrity = load_json(VALIDATION_DIR / "round4_model_integrity.json")
    shap = load_json(VALIDATION_DIR / "shap_requirement_status.json")
    tests_path = VALIDATION_DIR / "round4_test_results.json"
    if not tests_path.exists():
        tests_path.write_text(json.dumps({
            "python_version": environment["python_version"], "python_executable": environment["python_executable"],
            "tests_run": 0, "failures": 0, "errors": 0, "skipped": 0, "status": "PENDING",
        }, indent=2), encoding="utf-8")
    tests = load_json(tests_path)
    hotfix_tests = load_json(VALIDATION_DIR / "public_path_hotfix_test_results.json")

    assert contract["selected_engineered_feature_count"] >= 12
    assert candidate["Target Association Scope"].eq("release_year <= 2017").all()
    assert candidate["Target Association Builder Fit Scope"].eq("release_year <= 2017").all()
    assert candidate["Target Association Builder Fit Rows"].eq(coverage["selection_train"]["rows"]).all()
    assert leakage["Status"].eq("PASS").all() and feature_validation["Status"].eq("PASS").all()
    assert immutability["later_raw_distribution_changes_preserve_association_statistics"] is True
    assert selection["Fit Scope"].eq("selection train").all()
    assert selection["Evaluation Scope"].eq("validation 2018").all()
    eligible = selection.query("`Prediction Variant` == 'Clipped [0,100]'").sort_values(
        ["RMSE", "MAE", "Experiment", "Model"], kind="mergesort"
    )
    winner = eligible.iloc[0]
    assert winner["Experiment"] == lock["selection_winner_experiment"] == final_metrics["selection_winner_experiment"]
    assert winner["Model"] == lock["selection_winner_model"] == final_metrics["selection_winner_model"]
    assert lock["historically_never_observed_claim"] is False
    assert coverage["final_temporal_holdout"]["max_year"] == coverage["max_release_year"]
    assert coverage["product_support_end_year"] < coverage["max_release_year"]
    assert environment["status"] == "PASS" and environment["python_version"].startswith("3.12.")
    assert notebook_status["status"] == "PASS" and notebook_status["python_version"].startswith("3.12.")
    assert e2e["api_direct_prediction_parity"] is True
    assert e2e["prediction_support_policy"]["status"] == "PASS"
    assert e2e["prediction_support_policy"]["year_2020"]["prediction_support_status"] == "within_product_support"
    assert e2e["prediction_support_policy"]["year_2026"]["temporal_extrapolation"] is True
    assert e2e["streamlit"]["year_2020_warning_count"] == 0
    assert e2e["streamlit"]["year_2026_warning_count"] >= 1
    assert integrity["status"] == "PASS" and integrity["notebook_06_retrained"] is False
    if final_mode:
        assert tests["status"] == "PASS" and tests["skipped"] == 0
        assert tests["python_version"].startswith("3.12.")
        assert hotfix_tests["status"] == "PASS" and hotfix_tests["skipped"] == 0

    safe_reset_submission()
    for source_relative, destination_relative in COPY_MAP.items():
        source = ROOT / source_relative
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, SUBMISSION / destination_relative)
    (SUBMISSION / "GIT_EVIDENCE.md").write_text(collect_git_evidence(), encoding="utf-8")

    external_paths = [
        ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib",
        ROOT / "4.MODELS" / "hitradar_popularity" / "final_test_metrics.json",
        ROOT / "4.MODELS" / "hitradar_secondary" / "kmeans_pipeline.joblib",
        ROOT / "4.MODELS" / "hitradar_secondary" / "content_recommender.joblib",
        ROOT / "5.DATA" / "processed" / "ml_ready_dataset.csv",
        ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet",
        ROOT / "5.DATA" / "processed" / "features_engineered.parquet",
    ]
    external = []
    tracked_files = set(
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    ) if (ROOT / ".git").exists() else set()
    for path in external_paths:
        current_hash = digest(path)
        relative_path = path.relative_to(ROOT).as_posix()
        is_tracked = relative_path in tracked_files
        item = {
            "canonical_path": relative_path,
            "size_bytes": path.stat().st_size, "sha256": current_hash,
            "tracked_in_current_tree": is_tracked,
            "round4_note": (
                "tracked canonical evidence; not duplicated as a binary artifact in the snapshot"
                if is_tracked else
                "local external artifact omitted from the current tracked tree; legacy commits may contain historical copies because Git history was not rewritten"
            ),
        }
        if path == MODEL_DIR / "popularity_pipeline.joblib":
            item["pre_round4_sha256"] = integrity["production_model"]["pre_round4_sha256"]
            item["unchanged_from_pre_round4"] = current_hash == item["pre_round4_sha256"]
        external.append(item)
    (SUBMISSION / "evidence" / "external_artifact_checksums.json").write_text(
        json.dumps(external, indent=2), encoding="utf-8"
    )
    write_readme(final_metrics, coverage, integrity, shap)

    late_rows = pd.DataFrame([
        {"Year": int(year), "Rows": rows}
        for year, rows in coverage["rows_by_year"].items()
        if int(year) >= coverage["final_temporal_holdout"]["min_year"]
    ])
    notebook_table = pd.DataFrame(notebook_status["notebooks"])
    external_table = pd.DataFrame(external)[["canonical_path", "size_bytes", "sha256"]]
    clipped = final_metrics["clipped_test_metrics"]
    git_status = "verifiable from real Git metadata" if (ROOT / ".git").exists() else "not verifiable in this workspace"
    report = f"""# HitRadar Round 4 — Final Audit Report

Generated from current canonical JSON/CSV/notebook artifacts; no metric or year count is manually entered.

## A. Feature Engineering

- Candidates: **{contract['candidate_engineered_feature_count']}**; selected: **{contract['selected_engineered_feature_count']}**.
- Descriptive target association and redundancy use a separate selection-train builder fit on **{int(candidate['Target Association Builder Fit Rows'].iloc[0]):,}** rows with scope **{candidate['Target Association Builder Fit Scope'].iloc[0]}**.
- Target association remains descriptive rather than an automatic Keep/Drop rule.

## B. Leakage / Feature Contract

- Dependency audit: **PASS**; selected feature validation: **PASS**.
- Later 2018/2019+ raw distributions do not change audit-builder learned statistics: **PASS**.
- Validation/final target changes do not affect selection-train association: **PASS**.

## C. Temporal Model Selection

Selection train is `release_year <= 2017`; validation is 2018. Locked winner remains **{lock['selection_winner_experiment']} / {lock['selection_winner_model']}**.

## D. Final Evaluation

- Final refit: **{final_metrics['final_refit_scope']}**, {final_metrics['final_refit_rows']:,} rows.
- Final holdout: **{final_metrics['final_test_scope']}**, {final_metrics['final_test_rows']:,} rows.
- Deployed clipped metrics: MAE **{clipped['MAE']:.6f}**, RMSE **{clipped['RMSE']:.6f}**, R² **{clipped['R2']:.6f}**.
- Notebook 06 was not retrained; model and metrics artifact checksums are unchanged.

## E. Historical Holdout Caveat

{HISTORICAL_CAVEAT} The valid lock evidence is scoped to corrected Round 2.

## F. Temporal Year Coverage

- Canonical data: {coverage['total_rows']:,} rows, years **{coverage['min_release_year']}–{coverage['max_release_year']}**.
- Final holdout: {coverage['final_temporal_holdout']['rows']:,} rows, years **{coverage['final_temporal_holdout']['min_year']}–{coverage['final_temporal_holdout']['max_year']}**.

{markdown_table(late_rows, 0)}

Observed row coverage is not identical to validation quality or product support.

## G. Product Support Policy

The product support cutoff is **{coverage['product_support_end_year']}**, intentionally conservative and distinct from observed data max year **{coverage['max_release_year']}**. Year 2020 is `within_product_support`; year 2026 is `temporal_extrapolation`. Warning metadata does not change the numerical prediction.

## H. Clustering

Chosen k: **{cluster['chosen_k']}**; best silhouette: **{float(k_scores['Silhouette'].max()):.6f}**. Separation remains modest.

## I. Recommendation

Indexed rows: **{recommendation['rows']:,}**; self-exclusion: **{'PASS' if recommendation['self_excluded'] else 'FAIL'}**. {recommendation['metadata_limitation']}

## J. Deployment

- API/direct parity: **PASS**; health: **{e2e['health']['status']}**.
- API metadata distinguishes product support from observed/final-holdout max year.
- Streamlit AppTest: 2020 warnings **{e2e['streamlit']['year_2020_warning_count']}**; 2026 warnings **{e2e['streamlit']['year_2026_warning_count']}**; zero unhandled exceptions.

## K. Python 3.12 Environment Validation

- Python **{environment['python_version']}** at `{environment['python_executable']}`.
- pip **{environment['pip_version']}**, NumPy **{environment['numpy_version']}**, pandas **{environment['pandas_version']}**, sklearn **{environment['scikit_learn_version']}**, XGBoost **{environment['xgboost_version']}**, FastAPI **{environment['fastapi_version']}**, Starlette **{environment['starlette_version']}**, httpx2 **{environment['http_client_version']}**.
- Fresh requirements install: **{environment['requirements_install_status']}**; TestClient smoke: **{environment['fastapi_testclient_smoke']}**.

## L. Notebook Execution

Kernel: **{notebook_status['kernel_name']}**; Python **{notebook_status['python_version']}**.

{markdown_table(notebook_table, 0)}

## M. Automated Tests

Tests **{tests['tests_run']}**, failures **{tests['failures']}**, errors **{tests['errors']}**, skipped **{tests['skipped']}**, status **{tests['status']}**, Python **{tests['python_version']}**.

Public-path hotfix full suite: **{hotfix_tests['tests_run']}** tests, failures **{hotfix_tests['failures']}**, errors **{hotfix_tests['errors']}**, skipped **{hotfix_tests['skipped']}**, status **{hotfix_tests['status']}**.

## N. Final Submission Semantics

`FINAL_SUBMISSION` is a **submission/evidence snapshot**, not standalone runnable. Canonical repository, data, and external models remain required. Manifest metadata states these semantics explicitly.

## O. External Artifact Checksums

{markdown_table(external_table, 0)}

Production model unchanged from pre-Round-4 checksum: **{integrity['production_model']['unchanged']}**.

## P. Git Evidence

Git evidence is **{git_status}**; unavailable evidence is not labeled PASS.

## Q. SHAP Status

SHAP was not added because the readable checklist labels it as an advanced item, not an explicit mandatory requirement. Existing importance/error evidence is descriptive, not causal.

## R. Evidence Path Sanitization

Machine-specific absolute paths and local usernames are sanitized in the tracked repository and the public `FINAL_SUBMISSION` snapshot. Pre-sanitization raw evidence is retained only in ignored local storage under `scratch/private_evidence/`; it is excluded from the public package. Original and sanitized checksums are recorded for audit.

## S. Remaining Limitations

- Model performance is modest and the high-popularity tail remains difficult.
- Time variables are influential, increasing temporal-shift risk.
- Post-{coverage['product_support_end_year']} predictions are temporal extrapolations even when observed rows exist later.
- KMeans silhouette is modest; recommendation has no human relevance study or title/artist metadata.
- Git history and PR evidence are {git_status}.
"""
    assert_clean_generated_markdown(report)
    (SUBMISSION / "FINAL_AUDIT_REPORT.md").write_text(report, encoding="utf-8")

    configured_python = str(environment.get("python_executable", ""))
    public_python = current_python_path() if configured_python.startswith("<") else Path(configured_python)
    replacement_counts, sanitized_files = sanitize_submission_copies(public_python)
    scanned_before_report, findings_before_report = scan_public_tree(SUBMISSION)
    if findings_before_report:
        raise AssertionError(f"Sensitive public paths remain before sanitization report: {findings_before_report}")

    tracked_sanitized_after = snapshot_hashes(tuple(PRIVATE_RAW_BASELINE_SHA256))
    model_sha_after = digest(model_path)
    metrics_sha_after = digest(metrics_path)
    evidence_checks = [
        {
            "canonical_file": relative,
            "private_raw_sha256": private_raw_hashes[relative],
            "tracked_sanitized_sha256": tracked_sanitized_after[relative],
            "private_raw_copy_available_locally": True,
            "tracked_public_copy_sanitized": private_raw_hashes[relative] != tracked_sanitized_after[relative],
            "unchanged_during_generation": tracked_sanitized_before[relative] == tracked_sanitized_after[relative],
            "mutable_after_generation": relative.endswith("round4_test_results.json"),
        }
        for relative in PRIVATE_RAW_BASELINE_SHA256
    ]
    evidence_stable = all(item["unchanged_during_generation"] for item in evidence_checks)
    model_unchanged = model_sha_before == model_sha_after == integrity["production_model"]["pre_round4_sha256"]
    metrics_unchanged = metrics_sha_before == metrics_sha_after == integrity["final_metrics_artifact"]["pre_round4_sha256"]
    if not (evidence_stable and model_unchanged and metrics_unchanged):
        raise AssertionError("Tracked evidence, production model, or final metrics changed during package generation")

    sanitization_report = {
        "policy": "Tracked evidence is sanitized; private raw originals are retained only under ignored local scratch/private_evidence and excluded from the public repository.",
        "files_scanned": scanned_before_report + 2,
        "files_sanitized": len(sanitized_files),
        "sanitized_files": sanitized_files,
        "replacement_counts": replacement_counts,
        "tracked_evidence_sanitized": True,
        "private_raw_evidence_excluded": True,
        "evidence_checksums": evidence_checks,
        "public_submission_scan_passed": True,
        "remaining_sensitive_absolute_paths": [],
        "model_integrity": {
            "notebook_06_retrained": False,
            "model_sha256_before": model_sha_before,
            "model_sha256_after": model_sha_after,
            "model_unchanged": model_unchanged,
            "final_metrics_sha256_before": metrics_sha_before,
            "final_metrics_sha256_after": metrics_sha_after,
            "final_metrics_unchanged": metrics_unchanged,
            "clipped_test_metrics": final_metrics["clipped_test_metrics"],
        },
        "status": "PASS",
    }
    public_report_path = VALIDATION_DIR / "public_evidence_sanitization.json"
    public_report_text = json.dumps(sanitization_report, indent=2, ensure_ascii=False) + "\n"
    public_report_path.write_text(public_report_text, encoding="utf-8")
    (SUBMISSION / "evidence" / "public_evidence_sanitization.json").write_text(public_report_text, encoding="utf-8")
    scanned_before_manifest, findings_before_manifest = scan_public_tree(SUBMISSION)
    if findings_before_manifest:
        raise AssertionError(f"Sensitive public paths remain before manifest generation: {findings_before_manifest}")

    files_before_manifest = sorted(path for path in SUBMISSION.rglob("*") if path.is_file())
    offenders = [path.name for path in files_before_manifest if path.name.upper().startswith(LEGACY_PREFIXES)]
    requirement_files = [path for path in files_before_manifest if path.name.lower() == "requirements.txt"]
    assert not offenders and len(requirement_files) == 1
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "final" if final_mode else "prepare",
        "package_type": "submission_evidence_snapshot",
        "standalone_runnable": False,
        "canonical_repository_required": True,
        "external_artifacts_required": True,
        "public_path_sanitization": True,
        "tracked_evidence_sanitized": True,
        "private_raw_evidence_excluded": True,
        "file_count_excluding_manifest": len(files_before_manifest),
        "requirements_files": [str(path.relative_to(SUBMISSION)).replace("\\", "/") for path in requirement_files],
        "legacy_prefixed_files": offenders,
        "files": [
            {"path": str(path.relative_to(SUBMISSION)).replace("\\", "/"), "size_bytes": path.stat().st_size, "sha256": digest(path)}
            for path in files_before_manifest
        ],
    }
    (SUBMISSION / "SUBMISSION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    scanned_final, findings_final = scan_public_tree(SUBMISSION)
    if findings_final:
        raise AssertionError(f"Sensitive public paths remain after manifest generation: {findings_final}")
    if scanned_final != sanitization_report["files_scanned"]:
        raise AssertionError((scanned_final, sanitization_report["files_scanned"]))
    print(json.dumps({
        "submission": "FINAL_SUBMISSION", "mode": manifest["mode"],
        "files_including_manifest": len(files_before_manifest) + 1,
        "tests_status": tests["status"], "package_type": manifest["package_type"],
        "public_path_scan": {"files_scanned": scanned_final, "sensitive_matches": 0, "status": "PASS"},
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="Require passing Round-4 evidence.")
    main(final_mode=parser.parse_args().final)
