$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$destination = (Resolve-Path -LiteralPath "<PROJECT_ROOT>").Path
if ($destination -ne "<PROJECT_ROOT>") { throw "Unexpected destination: $destination" }
if ((Get-ChildItem -LiteralPath $destination -Directory).Count -gt 0) {
    throw "Review destination must remain flat."
}

$relativeFiles = @(
    ".gitignore",
    "src\features.py",
    "src\modeling.py",
    "src\evaluation.py",
    "src\secondary_tasks.py",
    "3.NOTEBOOKS\3.5.feature_engineering\05_feature_engineering.ipynb",
    "3.NOTEBOOKS\3.6.modeling\06_machine_learning.ipynb",
    "3.NOTEBOOKS\3.7.demo\07_ai_deployment.ipynb",
    "5.UNG_DUNG\5.1.backend_api\api.py",
    "5.UNG_DUNG\5.1.backend_api\models\prediction.py",
    "5.UNG_DUNG\5.2.frontend\streamlit_app.py",
    "5.UNG_DUNG\5.3.config\requirements.txt",
    "5.UNG_DUNG\5.3.config\RUNTIME_ENVIRONMENT.md",
    "tests\test_feature_pipeline.py",
    "scratch\execute_notebook.py",
    "scratch\build_notebooks_05_07.py",
    "9.SCRIPTS\run_round2_tests.py",
    "9.SCRIPTS\generate_round2_report.py",
    "ROUND2_FINAL_REPORT.md",
    "5.DATA\processed\features_engineered.parquet",
    "7.ML\7.6.feature_engineering\candidate_feature_register.csv",
    "7.ML\7.6.feature_engineering\candidate_feature_evaluation.csv",
    "7.ML\7.6.feature_engineering\feature_keep_drop_decisions.csv",
    "7.ML\7.6.feature_engineering\feature_dependency_leakage_audit.csv",
    "7.ML\7.6.feature_engineering\feature_validation.csv",
    "7.ML\7.6.feature_engineering\feature_contract.json",
    "7.ML\7.6.feature_engineering\train_statistics.json",
    "7.ML\7.6.feature_engineering\train_stat_immutability.json",
    "4.MODELS\hitradar_secondary\kmeans_pipeline.joblib",
    "4.MODELS\hitradar_secondary\kmeans_k_selection.csv",
    "4.MODELS\hitradar_secondary\kmeans_k_selection.png",
    "4.MODELS\hitradar_secondary\cluster_metadata.json",
    "4.MODELS\hitradar_secondary\cluster_profiles.csv",
    "4.MODELS\hitradar_secondary\cluster_profiles_by_decade.csv",
    "4.MODELS\hitradar_secondary\cluster_assignments.parquet",
    "4.MODELS\hitradar_secondary\content_recommender.joblib",
    "4.MODELS\hitradar_secondary\recommendation_examples.csv",
    "4.MODELS\hitradar_secondary\recommendation_metadata.json",
    "4.MODELS\hitradar_popularity\popularity_pipeline.joblib",
    "4.MODELS\hitradar_popularity\selection_winner_lock.json",
    "4.MODELS\hitradar_popularity\final_test_metrics.json",
    "4.MODELS\4.2.evaluation\model_selection_validation_metrics.csv",
    "4.MODELS\4.2.evaluation\validation_time_bias_comparison.csv",
    "4.MODELS\4.2.evaluation\final_error_groups.csv",
    "4.MODELS\4.2.evaluation\final_transformed_feature_importance.csv",
    "4.MODELS\4.2.evaluation\final_grouped_feature_importance.csv",
    "4.MODELS\4.2.evaluation\feature_builder_saved_parity.json",
    "4.MODELS\4.2.evaluation\pipeline_reload_parity.json",
    "4.MODELS\4.2.evaluation\temporal_partition_rows.csv",
    "4.MODELS\4.2.evaluation\final_test_predictions.parquet",
    "4.MODELS\4.2.evaluation\final_test_diagnostics.png",
    "5.UNG_DUNG\validation\round2_end_to_end_validation.json",
    "5.UNG_DUNG\validation\round2_test_results.json"
)

foreach ($relative in $relativeFiles) {
    $source = Join-Path $projectRoot $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing Round-2 handoff source: $source"
    }
    Copy-Item -LiteralPath $source -Destination (Join-Path $destination (Split-Path $relative -Leaf)) -Force
}

$files = Get-ChildItem -LiteralPath $destination -File | Sort-Object Name
$legacy = $files | Where-Object { $_.Name -match "^(HOTFIX|OUTPUT|BEFORE)_" }
$subfolders = Get-ChildItem -LiteralPath $destination -Directory
[pscustomobject]@{
    Files = $files.Count
    Subfolders = $subfolders.Count
    LegacyPrefixed = $legacy.Count
    TotalMB = [math]::Round((($files | Measure-Object Length -Sum).Sum / 1MB), 2)
}
$files | Select-Object Name, Length
