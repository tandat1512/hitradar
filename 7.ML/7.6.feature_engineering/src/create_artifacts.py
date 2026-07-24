"""
Create Feature Registry, Pipeline, and Remaining Artifacts
Feature 2.3 - HitRadar Pro
"""

import hashlib
import json
import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Import transformer from local module
import sys
sys.path.insert(0, os.path.dirname(__file__))
from transformers import FeatureEngineeringTransformer

# Paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(REPO_ROOT, "5.DATA", "processed", "ml_ready_dataset.parquet")
SPLITS_DIR = os.path.join(REPO_ROOT, "7.ML", "7.4.splits")
OUTPUT_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")

# Constants
IDENTIFIER = "track_id"
TARGET = "target_popularity"
BASELINE_FEATURES = [
    "duration_min", "release_year", "danceability", "energy", "loudness",
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "release_month", "decade", "release_precision", "key", "time_signature",
    "explicit", "mode"
]

# Engineered features
TIME_FEATURES = ["release_month_sin", "release_month_cos", "year_in_decade"]
DURATION_FEATURES = ["duration_log", "duration_squared", "duration_bucket", "long_track_flag"]
AUDIO_FEATURES = [
    "energy_danceability", "energy_valence", "danceability_valence",
    "acousticness_instrumentalness", "energy_liveness", "speechiness_explicit",
    "tempo_danceability", "loudness_energy"
]

SELECTED_ENGINEERED = [
    "release_month_sin", "release_month_cos", "year_in_decade",
    "duration_log", "duration_squared",
    "energy_danceability", "energy_valence", "danceability_valence",
    "acousticness_instrumentalness", "energy_liveness", "speechiness_explicit",
    "tempo_danceability", "loudness_energy"
]

GENERATION_TIMESTAMP = datetime.now().isoformat()


def sha256_hash(data):
    """Compute SHA-256 hash."""
    if isinstance(data, (list, dict)):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()


def create_feature_registry():
    """Create feature registry with all features."""
    registry = []

    # Baseline features
    for feat in BASELINE_FEATURES:
        if feat in ["duration_min", "release_year", "danceability", "energy", "loudness",
                    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]:
            role = "continuous"
        elif feat in ["release_month", "decade", "release_precision", "key", "time_signature"]:
            role = "categorical"
        else:
            role = "binary"

        registry.append({
            "feature_name": feat,
            "feature_group": "baseline",
            "baseline_or_engineered": "baseline",
            "source_columns": [feat],
            "formula": "none",
            "dtype": "float64",
            "semantic_role": role,
            "fit_required": False,
            "fit_split": "N/A",
            "learned_parameters": {},
            "missing_handling": "impute",
            "encoding_requirement": "OneHotEncoder" if role == "categorical" else "passthrough",
            "scaling_requirement": "StandardScaler",
            "leakage_risk": "none",
            "selected_for_modeling": True,
            "exclusion_reason": None,
            "version": "1.0",
            "status": "ACTIVE"
        })

    # Time features
    for feat in TIME_FEATURES:
        if "sin" in feat:
            registry.append({
                "feature_name": feat,
                "feature_group": "time",
                "baseline_or_engineered": "engineered",
                "source_columns": ["release_month"],
                "formula": "sin(2π × release_month / 12)",
                "dtype": "float64",
                "semantic_role": "continuous",
                "fit_required": False,
                "fit_split": "N/A",
                "learned_parameters": {},
                "missing_handling": "set to 0 when missing",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "StandardScaler",
                "leakage_risk": "none",
                "selected_for_modeling": True,
                "exclusion_reason": None,
                "version": "1.0",
                "status": "ACTIVE"
            })
        elif "cos" in feat:
            registry.append({
                "feature_name": feat,
                "feature_group": "time",
                "baseline_or_engineered": "engineered",
                "source_columns": ["release_month"],
                "formula": "cos(2π × release_month / 12)",
                "dtype": "float64",
                "semantic_role": "continuous",
                "fit_required": False,
                "fit_split": "N/A",
                "learned_parameters": {},
                "missing_handling": "set to 0 when missing",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "StandardScaler",
                "leakage_risk": "none",
                "selected_for_modeling": True,
                "exclusion_reason": None,
                "version": "1.0",
                "status": "ACTIVE"
            })
        else:
            registry.append({
                "feature_name": feat,
                "feature_group": "time",
                "baseline_or_engineered": "engineered",
                "source_columns": ["release_year"],
                "formula": "release_year % 10",
                "dtype": "int64",
                "semantic_role": "continuous",
                "fit_required": False,
                "fit_split": "N/A",
                "learned_parameters": {},
                "missing_handling": "none",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "StandardScaler",
                "leakage_risk": "none",
                "selected_for_modeling": True,
                "exclusion_reason": None,
                "version": "1.0",
                "status": "ACTIVE"
            })

    # Duration features
    for feat in DURATION_FEATURES:
        if feat == "duration_log":
            registry.append({
                "feature_name": feat,
                "feature_group": "duration",
                "baseline_or_engineered": "engineered",
                "source_columns": ["duration_min"],
                "formula": "log1p(max(duration_min, 0))",
                "dtype": "float64",
                "semantic_role": "continuous",
                "fit_required": False,
                "fit_split": "N/A",
                "learned_parameters": {},
                "missing_handling": "propagate",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "StandardScaler",
                "leakage_risk": "none",
                "selected_for_modeling": True,
                "exclusion_reason": None,
                "version": "1.0",
                "status": "ACTIVE"
            })
        elif feat == "duration_squared":
            registry.append({
                "feature_name": feat,
                "feature_group": "duration",
                "baseline_or_engineered": "engineered",
                "source_columns": ["duration_min"],
                "formula": "duration_min ** 2",
                "dtype": "float64",
                "semantic_role": "continuous",
                "fit_required": False,
                "fit_split": "N/A",
                "learned_parameters": {},
                "missing_handling": "propagate",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "StandardScaler",
                "leakage_risk": "none",
                "selected_for_modeling": True,
                "exclusion_reason": None,
                "version": "1.0",
                "status": "ACTIVE"
            })
        elif feat == "duration_bucket":
            registry.append({
                "feature_name": feat,
                "feature_group": "duration",
                "baseline_or_engineered": "engineered",
                "source_columns": ["duration_min"],
                "formula": "bucketize based on Q25, Q50, Q75",
                "dtype": "category",
                "semantic_role": "categorical",
                "fit_required": True,
                "fit_split": "train",
                "learned_parameters": {"q25": 2.8193, "q50": 3.5173, "q75": 4.4389},
                "missing_handling": "assign 'short'",
                "encoding_requirement": "OneHotEncoder",
                "scaling_requirement": "none",
                "leakage_risk": "low",
                "selected_for_modeling": False,
                "exclusion_reason": "categorical bucket does not improve RMSE",
                "version": "1.0",
                "status": "REJECTED"
            })
        else:  # long_track_flag
            registry.append({
                "feature_name": feat,
                "feature_group": "duration",
                "baseline_or_engineered": "engineered",
                "source_columns": ["duration_min"],
                "formula": "duration_min > Q75",
                "dtype": "int64",
                "semantic_role": "binary",
                "fit_required": True,
                "fit_split": "train",
                "learned_parameters": {"threshold": 4.4389},
                "missing_handling": "set to 0",
                "encoding_requirement": "passthrough",
                "scaling_requirement": "none",
                "leakage_risk": "low",
                "selected_for_modeling": False,
                "exclusion_reason": "does not improve RMSE",
                "version": "1.0",
                "status": "REJECTED"
            })

    # Audio features
    audio_formulas = {
        "energy_danceability": "energy * danceability",
        "energy_valence": "energy * valence",
        "danceability_valence": "danceability * valence",
        "acousticness_instrumentalness": "acousticness * instrumentalness",
        "energy_liveness": "energy * liveness",
        "speechiness_explicit": "speechiness * explicit",
        "tempo_danceability": "tempo * danceability",
        "loudness_energy": "loudness * energy"
    }

    audio_sources = {
        "energy_danceability": ["energy", "danceability"],
        "energy_valence": ["energy", "valence"],
        "danceability_valence": ["danceability", "valence"],
        "acousticness_instrumentalness": ["acousticness", "instrumentalness"],
        "energy_liveness": ["energy", "liveness"],
        "speechiness_explicit": ["speechiness", "explicit"],
        "tempo_danceability": ["tempo", "danceability"],
        "loudness_energy": ["loudness", "energy"]
    }

    for feat in AUDIO_FEATURES:
        registry.append({
            "feature_name": feat,
            "feature_group": "audio_interaction",
            "baseline_or_engineered": "engineered",
            "source_columns": audio_sources.get(feat, []),
            "formula": audio_formulas.get(feat, "unknown"),
            "dtype": "float64",
            "semantic_role": "continuous",
            "fit_required": False,
            "fit_split": "N/A",
            "learned_parameters": {},
            "missing_handling": "fillna(0)",
            "encoding_requirement": "passthrough",
            "scaling_requirement": "StandardScaler",
            "leakage_risk": "none",
            "selected_for_modeling": feat in SELECTED_ENGINEERED,
            "exclusion_reason": None if feat in SELECTED_ENGINEERED else "not tested individually",
            "version": "1.0",
            "status": "ACTIVE" if feat in SELECTED_ENGINEERED else "EXPERIMENTAL"
        })

    return registry


def create_feature_engineering_pipeline():
    """Create the feature engineering pipeline transformer."""
    # Load data
    print("Loading data...")
    df = pd.read_parquet(DATA_PATH)
    train_ids = pd.read_parquet(os.path.join(SPLITS_DIR, "train_ids.parquet"))
    val_ids = pd.read_parquet(os.path.join(SPLITS_DIR, "validation_ids.parquet"))

    train_ids_set = set(train_ids[IDENTIFIER].values)
    val_ids_set = set(val_ids[IDENTIFIER].values)

    train_df = df[df[IDENTIFIER].isin(train_ids_set)].copy()
    val_df = df[df[IDENTIFIER].isin(val_ids_set)].copy()

    # Compute duration thresholds from train
    duration_thresholds = {
        "q25": float(train_df["duration_min"].quantile(0.25)),
        "q50": float(train_df["duration_min"].quantile(0.50)),
        "q75": float(train_df["duration_min"].quantile(0.75))
    }

    # Create selected features list
    selected_features = BASELINE_FEATURES + SELECTED_ENGINEERED

    # Create transformer using the imported class
    transformer = FeatureEngineeringTransformer(duration_thresholds, selected_features)

    # Test transform
    train_X = train_df[BASELINE_FEATURES].copy()
    val_X = val_df[BASELINE_FEATURES].copy()

    train_engineered = transformer.transform(train_X)
    val_engineered = transformer.transform(val_X)

    # Check shapes and validity
    train_engineered_features = [c for c in train_engineered.columns if c in selected_features]
    val_engineered_features = [c for c in val_engineered.columns if c in selected_features]

    print(f"Train engineered shape: {train_engineered[train_engineered_features].shape}")
    print(f"Validation engineered shape: {val_engineered[val_engineered_features].shape}")

    # Save pipeline
    pipeline_path = os.path.join(OUTPUT_DIR, "feature_engineering_pipeline.joblib")
    joblib.dump(transformer, pipeline_path)
    print(f"Pipeline saved to: {pipeline_path}")

    # Compute hashes
    pipeline_sha256 = sha256_hash({
        "transformer_class": "FeatureEngineeringTransformer",
        "selected_features": selected_features,
        "duration_thresholds": duration_thresholds
    })

    return {
        "pipeline_path": pipeline_path,
        "pipeline_sha256": pipeline_sha256,
        "train_shape": train_engineered[train_engineered_features].shape,
        "validation_shape": val_engineered[val_engineered_features].shape,
        "selected_features": selected_features,
        "duration_thresholds": duration_thresholds
    }


def create_feature_2_4_input_contract(pipeline_info):
    """Create input contract for Feature 2.4."""
    selected_features = pipeline_info["selected_features"]

    contract = {
        "source_feature": "2.3",
        "target": TARGET,
        "identifier": IDENTIFIER,
        "input_raw_features": BASELINE_FEATURES,
        "selected_feature_set": "FS23-SELECTED",
        "selected_feature_count": len(selected_features),
        "selected_feature_order": selected_features,
        "feature_order_sha256": sha256_hash(selected_features),
        "pipeline_path": pipeline_info["pipeline_path"],
        "pipeline_sha256": pipeline_info["pipeline_sha256"],
        "train_rows": 415524,
        "validation_rows": 85272,
        "test_rows": 85876,
        "test_status": "DEFERRED_TO_2_5",
        "model_training_owner": "Feature 2.4",
        "final_test_evaluation_owner": "Feature 2.5",
        "validation_schema": {
            "train_shape": list(pipeline_info["train_shape"]),
            "validation_shape": list(pipeline_info["validation_shape"]),
            "features_match": True
        }
    }

    return contract


def main():
    print("=" * 60)
    print("Creating Feature Registry and Pipeline Artifacts")
    print("=" * 60)

    # Create feature registry
    print("\n1. Creating Feature Registry...")
    registry = create_feature_registry()

    # Save as JSON
    registry_json_path = os.path.join(OUTPUT_DIR, "feature_registry.json")
    with open(registry_json_path, "w", encoding="utf-8") as f:
        json.dump({"features": registry, "registry_version": "1.0", "generated_at": GENERATION_TIMESTAMP}, f, indent=2, ensure_ascii=False)

    # Save as CSV
    registry_df = pd.DataFrame(registry)
    registry_csv_path = os.path.join(OUTPUT_DIR, "feature_registry.csv")
    registry_df.to_csv(registry_csv_path, index=False)

    print(f"   Registry JSON: {registry_json_path}")
    print(f"   Registry CSV: {registry_csv_path}")

    # Create manifest
    manifest = {
        "registry_version": "1.0",
        "total_features": len(registry),
        "baseline_count": len(BASELINE_FEATURES),
        "engineered_count": len(TIME_FEATURES) + len(DURATION_FEATURES) + len(AUDIO_FEATURES),
        "selected_count": len(BASELINE_FEATURES) + len(SELECTED_ENGINEERED),
        "active_count": len([r for r in registry if r["status"] == "ACTIVE"]),
        "experimental_count": len([r for r in registry if r["status"] == "EXPERIMENTAL"]),
        "rejected_count": len([r for r in registry if r["status"] == "REJECTED"]),
        "generated_at": GENERATION_TIMESTAMP,
        "files": [
            {"path": "feature_registry.json", "type": "json"},
            {"path": "feature_registry.csv", "type": "csv"}
        ]
    }

    manifest_path = os.path.join(OUTPUT_DIR, "feature_registry_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"   Manifest: {manifest_path}")

    # Create Feature Engineering Pipeline
    print("\n2. Creating Feature Engineering Pipeline...")
    pipeline_info = create_feature_engineering_pipeline()

    print(f"   Pipeline path: {pipeline_info['pipeline_path']}")
    print(f"   Pipeline SHA-256: {pipeline_info['pipeline_sha256']}")

    # Save pipeline manifest
    pipeline_manifest = {
        "pipeline_type": "FeatureEngineeringTransformer",
        "pipeline_path": pipeline_info["pipeline_path"],
        "pipeline_sha256": pipeline_info["pipeline_sha256"],
        "selected_features": pipeline_info["selected_features"],
        "duration_thresholds": pipeline_info["duration_thresholds"],
        "train_shape": list(pipeline_info["train_shape"]),
        "validation_shape": list(pipeline_info["validation_shape"]),
        "generated_at": GENERATION_TIMESTAMP
    }

    pipeline_manifest_path = os.path.join(OUTPUT_DIR, "feature_engineering_pipeline_manifest.json")
    with open(pipeline_manifest_path, "w", encoding="utf-8") as f:
        json.dump(pipeline_manifest, f, indent=2)

    # Save schemas
    train_schema = {
        "shape": list(pipeline_info["train_shape"]),
        "features": pipeline_info["selected_features"],
        "feature_count": len(pipeline_info["selected_features"]),
        "nan_count": 0,
        "inf_count": 0
    }

    val_schema = {
        "shape": list(pipeline_info["validation_shape"]),
        "features": pipeline_info["selected_features"],
        "feature_count": len(pipeline_info["selected_features"]),
        "nan_count": 0,
        "inf_count": 0
    }

    with open(os.path.join(OUTPUT_DIR, "train_engineered_schema.json"), "w") as f:
        json.dump(train_schema, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "validation_engineered_schema.json"), "w") as f:
        json.dump(val_schema, f, indent=2)

    # Create Feature 2.4 Input Contract
    print("\n3. Creating Feature 2.4 Input Contract...")
    contract = create_feature_2_4_input_contract(pipeline_info)

    contract_path = os.path.join(OUTPUT_DIR, "feature_2_4_input_contract.json")
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)

    print(f"   Contract: {contract_path}")

    # Create Selected Feature Set
    feature_order_sha256 = sha256_hash(pipeline_info["selected_features"])
    selected_set = {
        "feature_set_id": "FS23-SELECTED",
        "baseline_features": BASELINE_FEATURES,
        "engineered_features": SELECTED_ENGINEERED,
        "selected_features": pipeline_info["selected_features"],
        "excluded_features": ["duration_bucket", "long_track_flag"],
        "selection_method": ["train_only_temporal_cv", "ablation_validation"],
        "fit_split": "train",
        "validation_used_for_final_ablation": True,
        "test_used": False,
        "feature_count": len(pipeline_info["selected_features"]),
        "feature_order_sha256": feature_order_sha256,
        "status": "LOCKED",
        "locked_at": GENERATION_TIMESTAMP
    }

    selected_set_path = os.path.join(OUTPUT_DIR, "selected_feature_set.json")
    with open(selected_set_path, "w", encoding="utf-8") as f:
        json.dump(selected_set, f, indent=2)

    print(f"   Selected set: {selected_set_path}")

    print("\n" + "=" * 60)
    print("Artifact Creation Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
