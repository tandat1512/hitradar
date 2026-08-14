"""Generate the canonical Round-2 report exclusively from current artifacts."""

from __future__ import annotations

import importlib.metadata as metadata
import json
from pathlib import Path
import subprocess
import sys

import nbformat
import pandas as pd
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_HOLDOUT_NOTE = (
    "The 2019+ horizon was not used for corrected Round-2 winner selection, "
    "but had been inspected during an earlier development iteration."
)
FE_DIR = ROOT / "7.ML" / "7.6.feature_engineering"
EVAL_DIR = ROOT / "4.MODELS" / "4.2.evaluation"
MODEL_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
SECONDARY_DIR = ROOT / "4.MODELS" / "hitradar_secondary"
VALIDATION_DIR = ROOT / "5.UNG_DUNG" / "validation"
ARCHIVE_DIR = ROOT / "10.ARCHIVE" / "pre_round2_20260813"
REVIEW_ARCHIVE_DIR = ROOT / "10.ARCHIVE" / "review_round1_flat"
REPORT_PATH = ROOT / "ROUND2_FINAL_REPORT.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def markdown_table(frame: pd.DataFrame, float_digits: int = 6) -> str:
    view = frame.copy()
    for column in view.select_dtypes(include="number").columns:
        view[column] = view[column].map(
            lambda value: f"{value:.{float_digits}f}" if pd.notna(value) else ""
        )
    headers = [str(column) for column in view.columns]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in view.astype(str).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


contract = load_json(FE_DIR / "feature_contract.json")
candidate_eval = pd.read_csv(FE_DIR / "candidate_feature_evaluation.csv")
feature_validation = pd.read_csv(FE_DIR / "feature_validation.csv")
dependency_audit = pd.read_csv(FE_DIR / "feature_dependency_leakage_audit.csv")
immutability = load_json(FE_DIR / "train_stat_immutability.json")
k_scores = pd.read_csv(SECONDARY_DIR / "kmeans_k_selection.csv")
cluster_meta = load_json(SECONDARY_DIR / "cluster_metadata.json")
cluster_profile = pd.read_csv(SECONDARY_DIR / "cluster_profiles.csv")
recommendation_meta = load_json(SECONDARY_DIR / "recommendation_metadata.json")
recommendation_examples = pd.read_csv(SECONDARY_DIR / "recommendation_examples.csv")
selection = pd.read_csv(EVAL_DIR / "model_selection_validation_metrics.csv")
time_bias = pd.read_csv(EVAL_DIR / "validation_time_bias_comparison.csv")
error_groups = pd.read_csv(EVAL_DIR / "final_error_groups.csv")
grouped_importance = pd.read_csv(EVAL_DIR / "final_grouped_feature_importance.csv")
final_metrics = load_json(MODEL_DIR / "final_test_metrics.json")
winner_lock = load_json(MODEL_DIR / "selection_winner_lock.json")
e2e = load_json(VALIDATION_DIR / "round2_end_to_end_validation.json")
tests = load_json(VALIDATION_DIR / "round2_test_results.json")

# Cross-artifact consistency assertions run before any report text is saved.
assert len(candidate_eval) == contract["candidate_engineered_feature_count"]
assert candidate_eval.query("Decision == 'KEEP'").shape[0] == contract["selected_engineered_feature_count"]
assert contract["selected_engineered_feature_count"] >= 12
assert feature_validation["Status"].eq("PASS").all()
assert dependency_audit["Status"].eq("PASS").all()
assert immutability["status"] == "PASS"
assert int(k_scores.loc[k_scores["Silhouette"].idxmax(), "k"]) == cluster_meta["chosen_k"]
assert recommendation_examples["query_track_id"].nunique() >= 3
assert not (recommendation_examples["query_track_id"] == recommendation_examples["track_id"]).any()
eligible = selection.query("`Prediction Variant` == 'Clipped [0,100]'").sort_values(
    ["RMSE", "MAE", "Experiment", "Model"], kind="mergesort"
)
artifact_winner = eligible.iloc[0]
assert artifact_winner["Experiment"] == winner_lock["selection_winner_experiment"] == final_metrics["selection_winner_experiment"]
assert artifact_winner["Model"] == winner_lock["selection_winner_model"] == final_metrics["selection_winner_model"]
assert final_metrics["winner_locked_before_final_test"]
assert winner_lock["final_test_labels_observed_before_round2_lock"] is False
assert winner_lock["historically_never_observed_claim"] is False
assert final_metrics["final_test_evaluation_count"] == 1
assert final_metrics["feature_builder_fit_rows"] == final_metrics["final_refit_rows"]
assert e2e["api_direct_prediction_parity"] is True
assert e2e["streamlit"]["status"] == "PASS"
assert tests["status"] == "PASS" and tests["skipped"] == 0

notebook_rows = []
for relative in [
    "3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb",
    "3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb",
    "3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb",
]:
    notebook = nbformat.read(ROOT / relative, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors = [output for cell in code_cells for output in cell.get("outputs", []) if output.get("output_type") == "error"]
    executed = sum(cell.get("execution_count") is not None for cell in code_cells)
    assert executed == len(code_cells) and not errors
    notebook_rows.append({"Notebook":Path(relative).name, "Code Cells":len(code_cells), "Executed":executed, "Errors":len(errors), "Status":"PASS"})
notebook_table = pd.DataFrame(notebook_rows)

packages = ["numpy", "pandas", "scikit-learn", "xgboost", "joblib", "pyarrow", "fastapi", "pydantic", "streamlit", "nbformat", "nbclient", "ipykernel"]
runtime_versions = {name: metadata.version(name) for name in packages}
kernel_specs = KernelSpecManager().find_kernel_specs()
kernel_ok = "hitradar-runtime" in kernel_specs
assert kernel_ok

git_available = (ROOT / ".git").exists()
git_evidence = "`.git` is absent; status, diff, branch and commits cannot be produced." 
if git_available:
    git_evidence = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True).stdout or "clean"

archived_project = sorted(str(path.relative_to(ARCHIVE_DIR)).replace("\\", "/") for path in ARCHIVE_DIR.rglob("*") if path.is_file()) if ARCHIVE_DIR.exists() else []
archived_review = sorted(path.name for path in REVIEW_ARCHIVE_DIR.glob("*") if path.is_file()) if REVIEW_ARCHIVE_DIR.exists() else []
dropped = candidate_eval.query("Decision == 'DROP'")[["Feature", "Max Raw Redundancy", "Decision Reason"]]
validation_clipped = selection.query("`Prediction Variant` == 'Clipped [0,100]'")[["Experiment", "Model", "MAE", "RMSE", "R2"]].sort_values(["RMSE", "MAE"])
cluster_sizes = cluster_profile[["cluster", "Rows"]].copy()
top_importance = grouped_importance.head(10)

raw_metrics = final_metrics["raw_test_metrics"]
prod_metrics = final_metrics["clipped_test_metrics"]
best_silhouette = float(k_scores["Silhouette"].max())

report = f"""# HitRadar Round 2 — Final Evaluation and Cleanup Report

Generated from canonical artifacts; no metric below is manually entered.

## A. Canonical files modified

- `src/features.py`, `src/evaluation.py`
- `3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb`
- `3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb`
- `3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb`
- `5.UNG_DUNG/5.1.backend_api/api.py`, `5.UNG_DUNG/5.1.backend_api/models/prediction.py`
- `5.UNG_DUNG/5.2.frontend/streamlit_app.py`
- `5.UNG_DUNG/5.3.config/requirements.txt`, `5.UNG_DUNG/5.3.config/RUNTIME_ENVIRONMENT.md`
- `tests/test_feature_pipeline.py`, `.gitignore`
- `scratch/execute_notebook.py`, `scratch/build_notebooks_05_07.py`, `scratch/copy_round2_review.ps1`
- `9.SCRIPTS/run_round2_tests.py`, `9.SCRIPTS/generate_round2_report.py`

Revalidated without unnecessary Round-2 rewrites: `src/modeling.py`, `src/secondary_tasks.py`.

## B. Archived stale files

{len(archived_project)} pre-Round-2 project files were moved under `10.ARCHIVE/pre_round2_20260813`; {len(archived_review)} old flat-review copies were moved under `10.ARCHIVE/review_round1_flat`. Active production and review directories contain only canonical current artifacts. Archived project paths include:\n\n""" + "\n".join(f"- `{path}`" for path in archived_project) + f"""

## C. Feature Engineering

- Candidates: **{contract['candidate_engineered_feature_count']}**
- Selected: **{contract['selected_engineered_feature_count']}** (requirement >=12: PASS)
- Dropped: **{len(dropped)}**
- Dependency leakage audit: **{contract['dependency_leakage_audit_status']}**
- Train-stat immutability/target independence: **{immutability['status']}**
- Final feature validation: **{'PASS' if feature_validation['Status'].eq('PASS').all() else 'FAIL'}**

{markdown_table(dropped)}

## D. Clustering

- Evaluated k range: **{int(k_scores['k'].min())}–{int(k_scores['k'].max())}**
- Chosen k: **{cluster_meta['chosen_k']}**
- Best sampled silhouette: **{best_silhouette:.6f}**
- Fit rows: **{cluster_meta['rows']:,}**

{markdown_table(cluster_sizes, 0)}

The ~{best_silhouette:.2f} silhouette indicates modest, not clearly separated, audio clusters. Target, popularity, identifiers and release time are excluded from cluster distance.

## E. Recommendation

- Rows indexed: **{recommendation_meta['rows']:,}**
- Metric: **{recommendation_meta['metric']}**
- Features: `{', '.join(recommendation_meta['features'])}`
- Saved query examples: **{recommendation_examples['query_track_id'].nunique()}**
- Self exclusion: **{'PASS' if recommendation_meta['self_excluded'] else 'FAIL'}**
- Metadata limitation: {recommendation_meta['metadata_limitation']}

## F. Model Selection — Validation 2018 only

Fit scope is `selection train`; evaluation scope is `validation 2018` for every row. Locked winner: **{winner_lock['selection_winner_experiment']} / {winner_lock['selection_winner_model']}**.

{markdown_table(validation_clipped)}

## G. Final Test — after lock and development refit

- Final refit: **{final_metrics['final_refit_scope']}**, {final_metrics['final_refit_rows']:,} rows
- Final test: **{final_metrics['final_test_scope']}**, {final_metrics['final_test_rows']:,} rows
- Evaluation count after lock: **{final_metrics['final_test_evaluation_count']}**
- Evaluation timestamp: `{final_metrics['final_test_evaluated_at_utc']}`

| Variant | MAE | RMSE | R² |
|---|---:|---:|---:|
| Raw model output | {raw_metrics['MAE']:.6f} | {raw_metrics['RMSE']:.6f} | {raw_metrics['R2']:.6f} |
| Production clipped [0,100] | {prod_metrics['MAE']:.6f} | {prod_metrics['RMSE']:.6f} | {prod_metrics['R2']:.6f} |

The production row matches deployed API behavior. Final-test results did not participate in configuration selection.

## G1. Historical holdout caveat

{HISTORICAL_HOLDOUT_NOTE} This preserves the valid lock-before-evaluation fact without making a project-wide historical claim.

## H. Time Bias — validation evidence

{markdown_table(time_bias)}

## I. Error Analysis — locked final pipeline on Final Test

Bias is Actual − Prediction; positive means underprediction.

{markdown_table(error_groups)}

High-popularity weakness is not hidden. Feature importance below is descriptive, not causal:

{markdown_table(top_importance)}

## J. Deployment

- Health: **{e2e['health']['status']}**; model loaded={e2e['health']['model_ready']}, cluster loaded={e2e['health']['cluster_ready']}, recommender loaded={e2e['health']['recommender_ready']}
- Direct pipeline/API prediction parity: **{'PASS' if e2e['api_direct_prediction_parity'] else 'FAIL'}**
- Cluster result: `{e2e['cluster']}`
- Recommendation self exclusion: **PASS**
- Streamlit tabs: `{', '.join(e2e['streamlit']['tabs'])}`; status **{e2e['streamlit']['status']}**

## K. Reproducibility

- Python: `{sys.version.split()[0]}`
- Kernel `hitradar-runtime` registered: **{kernel_ok}**
- Versions: """ + ", ".join(f"`{name}=={version}`" for name, version in runtime_versions.items()) + f"""

{markdown_table(notebook_table, 0)}

Fresh setup commands are documented in `5.UNG_DUNG/5.3.config/RUNTIME_ENVIRONMENT.md` and include explicit kernelspec registration.

## L. Tests

- Tests run: **{tests['tests_run']}**
- Failures: **{tests['failures']}**
- Errors: **{tests['errors']}**
- Skipped: **{tests['skipped']}**
- Status: **{tests['status']}**

## M. Git

{git_evidence}

This is **not verifiable in this workspace**, not a Git requirement PASS.

## N. Remaining limitations

- Popularity regression remains modest and the high-popularity tail remains difficult; no result was cosmetically optimized.
- Validation evidence may show strong dependence on time features; that improves historical holdout accuracy but raises temporal-shift risk.
- Engineered features are retained as a valid evaluated contract even if the validation winner is baseline.
- KMeans separation is modest at silhouette {best_silhouette:.6f}.
- Recommendation has no title/artist fields in the supplied ML-ready dataset and therefore returns truthful track IDs only.
- No external human relevance study was available for clusters or recommendations.
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(REPORT_PATH)
