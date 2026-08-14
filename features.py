"""Leakage-safe HitRadar feature engineering shared by notebooks and deployment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


RANDOM_STATE = 1512
TEST_START_YEAR = 2019
TARGET_ASSOCIATION_END_YEAR = 2017
TARGET_ASSOCIATION_SCOPE = "release_year <= 2017"
TARGET = "target_popularity"
IDENTIFIER = "track_id"

# The API/user supplies only these cleaned, non-engineered fields.
RAW_INPUT_FEATURES = [
    "duration_min",
    "explicit",
    "release_year",
    "release_month",
    "release_precision",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
]

BASELINE_NUMERIC_FEATURES = [
    "duration_min",
    "release_year",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "explicit",
    "mode",
]
BASELINE_CATEGORICAL_FEATURES = [
    "release_month",
    "decade",
    "release_precision",
    "key",
    "time_signature",
]
BASELINE_MODEL_FEATURES = BASELINE_NUMERIC_FEATURES + BASELINE_CATEGORICAL_FEATURES

# Candidates are implemented before evaluation. Selection is derived from the
# explicit evidence-backed drop registry below; there is no second hand-copied
# selected list that can drift away from the candidate evaluation.
CANDIDATE_ENGINEERED_NUMERIC_FEATURES = [
    "key_sin",
    "key_cos",
    "dance_energy",
    "positive_energy",
    "acoustic_energy_balance",
    "dance_valence",
    "acoustic_instrumental",
    "tempo_energy",
    "energy_vs_period_avg",
    "dance_vs_period_avg",
    "energy_loudness",
    "speechiness_log",
    "instrumentalness_log",
]
CANDIDATE_ENGINEERED_CATEGORICAL_FEATURES = [
    "mood_quadrant",
    "duration_category",
    "tempo_category",
]
CANDIDATE_ENGINEERED_FEATURES = (
    CANDIDATE_ENGINEERED_NUMERIC_FEATURES
    + CANDIDATE_ENGINEERED_CATEGORICAL_FEATURES
)

DROPPED_ENGINEERED_FEATURE_REASONS = {
    "speechiness_log": (
        "DROP only after the selection-train audit verifies near-exact monotonic "
        "rank redundancy (>=0.999) with retained raw speechiness; log1p adds no "
        "ordering information for the current model contract."
    ),
    "instrumentalness_log": (
        "DROP only after the selection-train audit verifies near-exact monotonic "
        "rank redundancy (>=0.999) with retained raw instrumentalness; log1p adds "
        "no ordering information for the current model contract."
    ),
}
SELECTED_ENGINEERED_FEATURES = [
    feature
    for feature in CANDIDATE_ENGINEERED_FEATURES
    if feature not in DROPPED_ENGINEERED_FEATURE_REASONS
]
SELECTED_ENGINEERED_NUMERIC_FEATURES = [
    feature
    for feature in CANDIDATE_ENGINEERED_NUMERIC_FEATURES
    if feature in SELECTED_ENGINEERED_FEATURES
]
SELECTED_ENGINEERED_CATEGORICAL_FEATURES = [
    feature
    for feature in CANDIDATE_ENGINEERED_CATEGORICAL_FEATURES
    if feature in SELECTED_ENGINEERED_FEATURES
]
MODEL_FEATURES = BASELINE_MODEL_FEATURES + SELECTED_ENGINEERED_FEATURES

FEATURE_DEPENDENCIES = {
    "key_sin": {"key"},
    "key_cos": {"key"},
    "dance_energy": {"danceability", "energy"},
    "positive_energy": {"valence", "energy"},
    "acoustic_energy_balance": {"acousticness", "energy"},
    "dance_valence": {"danceability", "valence"},
    "acoustic_instrumental": {"acousticness", "instrumentalness"},
    "tempo_energy": {"tempo", "energy"},
    "energy_vs_period_avg": {"energy", "release_year"},
    "dance_vs_period_avg": {"danceability", "release_year"},
    "energy_loudness": {"energy", "loudness"},
    "speechiness_log": {"speechiness"},
    "instrumentalness_log": {"instrumentalness"},
    "mood_quadrant": {"energy", "valence"},
    "duration_category": {"duration_min"},
    "tempo_category": {"tempo"},
}
LEARNED_STATISTIC_FEATURES = {
    "energy_vs_period_avg",
    "dance_vs_period_avg",
    "duration_category",
    "tempo_category",
}
FORBIDDEN_ENGINEERED_DEPENDENCIES = {
    TARGET,
    IDENTIFIER,
    "popularity",
    "label",
    "prediction",
    "residual",
}

FEATURE_KEEP_JUSTIFICATIONS = {
    "key_sin": "KEEP: first coordinate of a two-dimensional cyclic key representation.",
    "key_cos": "KEEP: complementary coordinate preserves key-cycle geometry with key_sin.",
    "dance_energy": "KEEP: nonlinear danceability-by-energy interaction for additive model classes.",
    "positive_energy": "KEEP: nonlinear valence-by-energy interaction representing positive intensity.",
    "acoustic_energy_balance": "KEEP: bounded relative balance, not a claim of low source correlation.",
    "dance_valence": "KEEP: nonlinear danceability-by-valence interaction motivated by binned EDA.",
    "acoustic_instrumental": "KEEP: joint acoustic/instrumental texture signal despite source correlation.",
    "tempo_energy": "KEEP: speed-by-energy interaction can expose intensity unavailable additively.",
    "energy_vs_period_avg": "KEEP: contextual deviation from train-only decade energy reference.",
    "dance_vs_period_avg": "KEEP: contextual deviation from train-only decade dance reference.",
    "energy_loudness": "KEEP: explicit energy-by-loudness interaction; high correlation is acknowledged.",
    "mood_quadrant": "KEEP: interpretable categorical regime using normalized domain midpoints.",
    "duration_category": "KEEP: train-quantile duration regime captures nonlinear duration behavior.",
    "tempo_category": "KEEP: train-quantile tempo regime captures nonlinear tempo behavior.",
}

# Backward-compatible names used by earlier review tests. Selection code and
# contracts use the explicit CANDIDATE/SELECTED constants above.
ENGINEERED_NUMERIC_FEATURES = SELECTED_ENGINEERED_NUMERIC_FEATURES
ENGINEERED_CATEGORICAL_FEATURES = SELECTED_ENGINEERED_CATEGORICAL_FEATURES
EXPECTED_ENGINEERED_FEATURES = SELECTED_ENGINEERED_FEATURES

TIME_DEPENDENT_MODEL_FEATURES = [
    "release_year",
    "release_month",
    "decade",
    "release_precision",
    "energy_vs_period_avg",
    "dance_vs_period_avg",
]

# Secondary-task contracts. No target, identifier or direct time variable is
# used in clustering distance or recommendation similarity.
CLUSTER_FEATURES = [
    "duration_min",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]
RECOMMENDATION_FEATURES = [
    "duration_min",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "key_sin",
    "key_cos",
]


def get_model_features(*, include_engineered: bool, include_time: bool) -> list[str]:
    """Return the exact pre-encoding model feature list for an experiment."""
    features = list(BASELINE_MODEL_FEATURES)
    if include_engineered:
        features += SELECTED_ENGINEERED_FEATURES
    if not include_time:
        features = [f for f in features if f not in TIME_DEPENDENT_MODEL_FEATURES]
    return features


def audit_feature_dependencies() -> pd.DataFrame:
    """Programmatically reject target-, identifier-, or label-derived candidates."""
    if set(FEATURE_DEPENDENCIES) != set(CANDIDATE_ENGINEERED_FEATURES):
        missing = set(CANDIDATE_ENGINEERED_FEATURES).difference(FEATURE_DEPENDENCIES)
        extra = set(FEATURE_DEPENDENCIES).difference(CANDIDATE_ENGINEERED_FEATURES)
        raise AssertionError(f"Dependency registry mismatch; missing={missing}, extra={extra}")
    rows = []
    for feature in CANDIDATE_ENGINEERED_FEATURES:
        dependencies = set(FEATURE_DEPENDENCIES[feature])
        forbidden = sorted(dependencies.intersection(FORBIDDEN_ENGINEERED_DEPENDENCIES))
        unknown = sorted(dependencies.difference(RAW_INPUT_FEATURES))
        passed = not forbidden and not unknown
        rows.append(
            {
                "Feature": feature,
                "Dependencies": ", ".join(sorted(dependencies)),
                "Forbidden Dependencies": ", ".join(forbidden),
                "Unknown Dependencies": ", ".join(unknown),
                "Audit Type": "Automated dependency audit",
                "Status": "PASS" if passed else "FAIL",
            }
        )
    return pd.DataFrame(rows)


def selection_train_association_index(
    frame: pd.DataFrame,
    *,
    max_rows: int = 120_000,
    random_state: int = RANDOM_STATE,
) -> pd.Index:
    """Return a deterministic sample drawn only from the pre-validation period."""
    if "release_year" not in frame.columns:
        raise ValueError("Target-association input is missing release_year.")
    year = pd.to_numeric(frame["release_year"], errors="coerce")
    eligible = frame.index[year <= TARGET_ASSOCIATION_END_YEAR]
    if len(eligible) == 0:
        raise ValueError("Target-association selection-train scope is empty.")
    if len(eligible) <= max_rows:
        return eligible
    return frame.loc[eligible].sample(max_rows, random_state=random_state).index


def _target_association(series: pd.Series, target: pd.Series) -> float:
    """Compute absolute Spearman for numeric data or correlation ratio for categories."""
    if pd.api.types.is_numeric_dtype(series):
        value = pd.to_numeric(series, errors="coerce").corr(target, method="spearman")
        return abs(float(value)) if pd.notna(value) else 0.0
    temp = pd.DataFrame(
        {"feature": series.astype("string"), "target": target}
    ).dropna()
    if temp.empty:
        return 0.0
    grand_mean = temp["target"].mean()
    between = sum(
        len(group) * (group["target"].mean() - grand_mean) ** 2
        for _, group in temp.groupby("feature", observed=True)
    )
    total = ((temp["target"] - grand_mean) ** 2).sum()
    return float(np.sqrt(between / total)) if total else 0.0


def candidate_target_associations(
    frame: pd.DataFrame,
    candidate_matrix: pd.DataFrame,
    *,
    target_column: str = TARGET,
    features: list[str] | None = None,
    max_rows: int = 120_000,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Calculate descriptive candidate associations on selection train only.

    Validation-2018 and final-2019+ labels are excluded by construction. These
    values are descriptive evidence and are not an automatic Keep/Drop rule.
    """
    if target_column not in frame.columns:
        raise ValueError(f"Target-association input is missing {target_column}.")
    if not frame.index.equals(candidate_matrix.index):
        raise ValueError("Raw frame and candidate matrix indexes must match.")
    selected_features = features or list(CANDIDATE_ENGINEERED_FEATURES)
    missing = [feature for feature in selected_features if feature not in candidate_matrix]
    if missing:
        raise ValueError(f"Candidate matrix is missing features: {missing}")
    audit_index = selection_train_association_index(
        frame, max_rows=max_rows, random_state=random_state
    )
    target = pd.to_numeric(frame.loc[audit_index, target_column], errors="coerce")
    rows = [
        {
            "Feature": feature,
            "Target Association": _target_association(
                candidate_matrix.loc[audit_index, feature], target
            ),
            "Target Association Scope": TARGET_ASSOCIATION_SCOPE,
            "Target Association Rows": int(len(audit_index)),
        }
        for feature in selected_features
    ]
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class FeatureStatistics:
    """Serializable audit view of learned train-only statistics."""

    duration_q33: float
    duration_q67: float
    tempo_q25: float
    tempo_q50: float
    tempo_q75: float
    mood_energy_midpoint: float
    mood_valence_midpoint: float
    global_energy_mean: float
    global_dance_mean: float
    fit_row_count: int


def _as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


class FeatureBuilder(BaseEstimator, TransformerMixin):
    """Create baseline and engineered features without target leakage.

    ``fit`` learns numeric fallbacks, duration/tempo thresholds and historical
    decade-level means from the training split only. ``transform`` applies the
    frozen statistics to train, test and online inference rows.
    """

    def __init__(self, include_engineered: bool = True, epsilon: float = 1e-6):
        self.include_engineered = include_engineered
        self.epsilon = epsilon

    def _validate_raw_columns(self, X: pd.DataFrame) -> None:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("FeatureBuilder expects a pandas DataFrame.")
        missing = [column for column in RAW_INPUT_FEATURES if column not in X.columns]
        if missing:
            raise ValueError(f"Missing raw input features: {missing}")

    def fit(self, X: pd.DataFrame, y: Any = None):
        self._validate_raw_columns(X)
        raw = X[RAW_INPUT_FEATURES].copy()

        numeric_sources = [
            "duration_min",
            "release_year",
            "release_month",
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
        ]
        self.numeric_fill_values_ = {}
        for column in numeric_sources:
            values = _as_numeric(raw[column])
            median = values.median()
            self.numeric_fill_values_[column] = float(median) if pd.notna(median) else 0.0

        duration = _as_numeric(raw["duration_min"]).fillna(
            self.numeric_fill_values_["duration_min"]
        )
        q33, q67 = duration.quantile([1 / 3, 2 / 3]).tolist()
        if not q33 < q67:
            q33, q67 = float(duration.min()), float(duration.max())
            if not q33 < q67:
                q67 = q33 + self.epsilon
        self.duration_thresholds_ = {"q33": float(q33), "q67": float(q67)}

        tempo = _as_numeric(raw["tempo"]).fillna(self.numeric_fill_values_["tempo"])
        tq25, tq50, tq75 = tempo.quantile([0.25, 0.50, 0.75]).tolist()
        if not tq25 < tq50 < tq75:
            raise ValueError("Train-only tempo quantiles are not strictly increasing.")
        self.tempo_thresholds_ = {
            "q25": float(tq25),
            "q50": float(tq50),
            "q75": float(tq75),
        }

        # Spotify energy/valence are normalized to [0, 1]. The fixed 0.5
        # threshold is the interpretable domain midpoint, not a learned target statistic.
        self.mood_thresholds_ = {"energy": 0.5, "valence": 0.5}

        release_year = _as_numeric(raw["release_year"]).fillna(
            self.numeric_fill_values_["release_year"]
        )
        period = (release_year // 10 * 10).astype(int)
        energy = _as_numeric(raw["energy"]).fillna(self.numeric_fill_values_["energy"])
        dance = _as_numeric(raw["danceability"]).fillna(
            self.numeric_fill_values_["danceability"]
        )
        period_frame = pd.DataFrame(
            {"period": period, "energy": energy, "danceability": dance},
            index=raw.index,
        )
        self.energy_period_means_ = (
            period_frame.groupby("period", observed=True)["energy"].mean().to_dict()
        )
        self.dance_period_means_ = (
            period_frame.groupby("period", observed=True)["danceability"].mean().to_dict()
        )
        self.global_energy_mean_ = float(energy.mean())
        self.global_dance_mean_ = float(dance.mean())
        self.fit_row_count_ = int(len(raw))
        self.feature_names_in_ = np.asarray(RAW_INPUT_FEATURES, dtype=object)
        return self

    def _build_all_features(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(
            self,
            [
                "numeric_fill_values_",
                "duration_thresholds_",
                "tempo_thresholds_",
                "mood_thresholds_",
                "energy_period_means_",
                "dance_period_means_",
            ],
        )
        self._validate_raw_columns(X)
        raw = X[RAW_INPUT_FEATURES].copy()

        def filled(column: str) -> pd.Series:
            return _as_numeric(raw[column]).fillna(self.numeric_fill_values_[column])

        duration = filled("duration_min")
        release_year = filled("release_year")
        danceability = filled("danceability")
        energy = filled("energy")
        key = filled("key")
        loudness = filled("loudness")
        speechiness = filled("speechiness")
        acousticness = filled("acousticness")
        instrumentalness = filled("instrumentalness")
        valence = filled("valence")
        tempo = filled("tempo")
        decade = (release_year // 10 * 10).astype(int)

        result = raw.copy()
        result["decade"] = decade
        result["key_sin"] = np.sin(2 * np.pi * (key % 12) / 12.0)
        result["key_cos"] = np.cos(2 * np.pi * (key % 12) / 12.0)
        result["dance_energy"] = danceability * energy
        result["positive_energy"] = valence * energy
        result["acoustic_energy_balance"] = acousticness / (
            acousticness + energy + self.epsilon
        )
        result["dance_valence"] = danceability * valence
        result["acoustic_instrumental"] = acousticness * instrumentalness
        result["tempo_energy"] = tempo * energy
        result["energy_loudness"] = energy * loudness
        result["speechiness_log"] = np.log1p(np.maximum(speechiness, 0.0))
        result["instrumentalness_log"] = np.log1p(
            np.maximum(instrumentalness, 0.0)
        )

        energy_mid = self.mood_thresholds_["energy"]
        valence_mid = self.mood_thresholds_["valence"]
        result["mood_quadrant"] = np.select(
            [
                (energy >= energy_mid) & (valence >= valence_mid),
                (energy >= energy_mid) & (valence < valence_mid),
                (energy < energy_mid) & (valence >= valence_mid),
            ],
            ["high_energy_positive", "high_energy_dark", "calm_positive"],
            default="calm_dark",
        )
        result["duration_category"] = pd.cut(
            duration,
            bins=[
                -np.inf,
                self.duration_thresholds_["q33"],
                self.duration_thresholds_["q67"],
                np.inf,
            ],
            labels=["short", "standard", "long"],
            include_lowest=True,
        ).astype("string")
        result["tempo_category"] = pd.cut(
            tempo,
            bins=[
                -np.inf,
                self.tempo_thresholds_["q25"],
                self.tempo_thresholds_["q50"],
                self.tempo_thresholds_["q75"],
                np.inf,
            ],
            labels=["slow", "moderate", "fast", "very_fast"],
            include_lowest=True,
        ).astype("string")

        energy_reference = decade.map(self.energy_period_means_).fillna(
            self.global_energy_mean_
        )
        dance_reference = decade.map(self.dance_period_means_).fillna(
            self.global_dance_mean_
        )
        result["energy_vs_period_avg"] = energy - energy_reference
        result["dance_vs_period_avg"] = danceability - dance_reference
        return result

    def transform_candidates(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return baseline plus every implemented candidate for NB05 evaluation."""
        result = self._build_all_features(X)
        return result[BASELINE_MODEL_FEATURES + CANDIDATE_ENGINEERED_FEATURES].copy()

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        result = self._build_all_features(X)
        output_columns = MODEL_FEATURES if self.include_engineered else BASELINE_MODEL_FEATURES
        return result[output_columns].copy()

    def get_feature_names_out(self, input_features=None) -> np.ndarray:
        features = MODEL_FEATURES if self.include_engineered else BASELINE_MODEL_FEATURES
        return np.asarray(features, dtype=object)

    def get_learned_statistics(self) -> dict[str, Any]:
        check_is_fitted(self, ["duration_thresholds_", "tempo_thresholds_", "fit_row_count_"])
        stats = FeatureStatistics(
            duration_q33=self.duration_thresholds_["q33"],
            duration_q67=self.duration_thresholds_["q67"],
            tempo_q25=self.tempo_thresholds_["q25"],
            tempo_q50=self.tempo_thresholds_["q50"],
            tempo_q75=self.tempo_thresholds_["q75"],
            mood_energy_midpoint=self.mood_thresholds_["energy"],
            mood_valence_midpoint=self.mood_thresholds_["valence"],
            global_energy_mean=self.global_energy_mean_,
            global_dance_mean=self.global_dance_mean_,
            fit_row_count=self.fit_row_count_,
        )
        result = asdict(stats)
        result["energy_period_means"] = {
            str(key): float(value) for key, value in self.energy_period_means_.items()
        }
        result["dance_period_means"] = {
            str(key): float(value) for key, value in self.dance_period_means_.items()
        }
        return result


def validate_selected_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return the final mandatory validation table for selected features."""
    dependency_status = audit_feature_dependencies().set_index("Feature")["Status"]
    rows = []
    for feature in SELECTED_ENGINEERED_FEATURES:
        exists = feature in df.columns
        if exists:
            series = df[feature]
            missing_count = int(series.isna().sum())
            infinite_count = (
                int(np.isinf(series.to_numpy(dtype=float)).sum())
                if pd.api.types.is_numeric_dtype(series)
                else 0
            )
            dtype = str(series.dtype)
        else:
            missing_count = None
            infinite_count = None
            dtype = "MISSING"
        leakage_check = (
            "Automated PASS"
            if dependency_status.get(feature) == "PASS"
            else "Automated FAIL"
        )
        selected = feature in SELECTED_ENGINEERED_FEATURES
        passed = (
            exists
            and missing_count == 0
            and infinite_count == 0
            and leakage_check == "Automated PASS"
            and selected
        )
        rows.append(
            {
                "Feature": feature,
                "Exists": exists,
                "Dtype": dtype,
                "Missing Count": missing_count,
                "Infinite Count": infinite_count,
                "Leakage Check": leakage_check,
                "Decision": "KEEP" if selected else "DROP",
                "Status": "PASS" if passed else "FAIL",
            }
        )
    return pd.DataFrame(rows)


def validate_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible alias for final selected feature validation."""
    return validate_selected_engineered_features(df)


def build_feature_contract() -> dict[str, Any]:
    dependency_audit = audit_feature_dependencies()
    return {
        "raw_input_features": RAW_INPUT_FEATURES,
        "baseline_model_features": BASELINE_MODEL_FEATURES,
        "candidate_engineered_features": CANDIDATE_ENGINEERED_FEATURES,
        "selected_engineered_features": SELECTED_ENGINEERED_FEATURES,
        "dropped_engineered_feature_reasons": DROPPED_ENGINEERED_FEATURE_REASONS,
        "feature_dependencies": {
            feature: sorted(dependencies)
            for feature, dependencies in FEATURE_DEPENDENCIES.items()
        },
        "learned_statistic_features": sorted(LEARNED_STATISTIC_FEATURES),
        "dependency_leakage_audit_status": (
            "PASS" if dependency_audit["Status"].eq("PASS").all() else "FAIL"
        ),
        "model_features": MODEL_FEATURES,
        "cluster_features": CLUSTER_FEATURES,
        "recommendation_features": RECOMMENDATION_FEATURES,
        "candidate_engineered_feature_count": len(CANDIDATE_ENGINEERED_FEATURES),
        "selected_engineered_feature_count": len(SELECTED_ENGINEERED_FEATURES),
        "target_association_scope": TARGET_ASSOCIATION_SCOPE,
        "test_start_year": TEST_START_YEAR,
        "target": TARGET,
        "target_note": (
            "target_popularity is the internal ML target name corresponding to "
            "Spotify popularity (0-100)."
        ),
        "identifier": IDENTIFIER,
        "cluster_is_model_feature": False,
        "target_is_model_feature": False,
    }
