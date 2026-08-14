"""Shared clustering and content-based recommendation for HitRadar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features import (
    CLUSTER_FEATURES,
    IDENTIFIER,
    RANDOM_STATE,
    RECOMMENDATION_FEATURES,
    FeatureBuilder,
)


@dataclass
class RecommendationBundle:
    """Serializable nearest-neighbor search bundle."""

    feature_builder: FeatureBuilder
    imputer: SimpleImputer
    scaler: StandardScaler
    neighbors: NearestNeighbors
    matrix: np.ndarray
    track_ids: np.ndarray
    feature_names: list[str]


def _finite_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return frame[columns].apply(pd.to_numeric, errors="coerce").replace(
        [np.inf, -np.inf], np.nan
    )


def select_kmeans_k(
    frame: pd.DataFrame,
    *,
    k_values=range(2, 11),
    fit_sample_size: int = 30_000,
    silhouette_sample_size: int = 5_000,
) -> tuple[pd.DataFrame, int]:
    """Evaluate k=2..10 on a deterministic sample and choose max silhouette."""
    data = _finite_frame(frame, CLUSTER_FEATURES)
    sampled = data.sample(min(fit_sample_size, len(data)), random_state=RANDOM_STATE)
    prep = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    matrix = prep.fit_transform(sampled)
    rows: list[dict[str, float | int]] = []
    for k in k_values:
        model = KMeans(n_clusters=int(k), n_init=10, random_state=RANDOM_STATE)
        labels = model.fit_predict(matrix)
        score = silhouette_score(
            matrix,
            labels,
            sample_size=min(silhouette_sample_size, len(matrix)),
            random_state=RANDOM_STATE,
        )
        rows.append({"k": int(k), "Inertia": float(model.inertia_), "Silhouette": float(score)})
    scores = pd.DataFrame(rows)
    chosen_k = int(scores.loc[scores["Silhouette"].idxmax(), "k"])
    return scores, chosen_k


def fit_cluster_pipeline(frame: pd.DataFrame, chosen_k: int) -> Pipeline:
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "kmeans",
                KMeans(n_clusters=int(chosen_k), n_init=10, random_state=RANDOM_STATE),
            ),
        ]
    )
    pipeline.fit(_finite_frame(frame, CLUSTER_FEATURES))
    return pipeline


def predict_cluster(cluster_pipeline: Pipeline, raw: pd.DataFrame) -> np.ndarray:
    return cluster_pipeline.predict(_finite_frame(raw, CLUSTER_FEATURES))


def cluster_profiles(
    frame: pd.DataFrame, labels: np.ndarray
) -> tuple[pd.DataFrame, pd.DataFrame]:
    profiled = frame.copy()
    profiled["cluster"] = np.asarray(labels, dtype=int)
    profile = (
        profiled.groupby("cluster", observed=True)[CLUSTER_FEATURES]
        .mean()
        .assign(Rows=profiled.groupby("cluster", observed=True).size())
        .reset_index()
    )
    decade = (pd.to_numeric(profiled["release_year"], errors="coerce") // 10 * 10).astype(
        "Int64"
    )
    by_decade = (
        profiled.assign(decade=decade)
        .groupby(["decade", "cluster"], observed=True)
        .size()
        .rename("Rows")
        .reset_index()
    )
    by_decade["Share Within Decade"] = by_decade["Rows"] / by_decade.groupby(
        "decade", observed=True
    )["Rows"].transform("sum")
    return profile, by_decade


def fit_recommender(
    raw: pd.DataFrame,
    track_ids: pd.Series | np.ndarray,
    *,
    feature_builder: FeatureBuilder | None = None,
) -> RecommendationBundle:
    """Fit cosine neighbors using audio content only (never target/popularity)."""
    builder = feature_builder or FeatureBuilder(include_engineered=True).fit(raw)
    candidates = builder.transform_candidates(raw)
    audio = _finite_frame(candidates, RECOMMENDATION_FEATURES)
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    matrix = scaler.fit_transform(imputer.fit_transform(audio)).astype(np.float32)
    neighbors = NearestNeighbors(metric="cosine", algorithm="brute", n_jobs=-1)
    neighbors.fit(matrix)
    ids = np.asarray(track_ids).astype(str)
    if len(ids) != len(matrix):
        raise ValueError("track_ids and recommendation matrix have different lengths.")
    if pd.Series(ids).duplicated().any():
        raise ValueError("track_id must be unique for deterministic recommendation lookup.")
    return RecommendationBundle(
        feature_builder=builder,
        imputer=imputer,
        scaler=scaler,
        neighbors=neighbors,
        matrix=matrix,
        track_ids=ids,
        feature_names=list(RECOMMENDATION_FEATURES),
    )


def recommend_by_track_id(
    bundle: RecommendationBundle, track_id: str, n_recommendations: int = 5
) -> pd.DataFrame:
    """Return nearest tracks, explicitly excluding the query track itself."""
    positions = np.flatnonzero(bundle.track_ids == str(track_id))
    if len(positions) == 0:
        raise KeyError(f"Unknown track_id: {track_id}")
    query_position = int(positions[0])
    requested = min(int(n_recommendations) + 1, len(bundle.track_ids))
    distances, indices = bundle.neighbors.kneighbors(
        bundle.matrix[query_position : query_position + 1], n_neighbors=requested
    )
    rows: list[dict[str, Any]] = []
    for distance, position in zip(distances[0], indices[0]):
        candidate_id = str(bundle.track_ids[int(position)])
        if candidate_id == str(track_id):
            continue
        rows.append(
            {
                "track_id": candidate_id,
                "cosine_similarity": float(1.0 - distance),
            }
        )
        if len(rows) == n_recommendations:
            break
    return pd.DataFrame(rows)


def recommend_from_raw(
    bundle: RecommendationBundle, raw: pd.DataFrame, n_recommendations: int = 5
) -> pd.DataFrame:
    candidates = bundle.feature_builder.transform_candidates(raw)
    audio = _finite_frame(candidates, bundle.feature_names)
    matrix = bundle.scaler.transform(bundle.imputer.transform(audio)).astype(np.float32)
    requested = min(int(n_recommendations), len(bundle.track_ids))
    distances, indices = bundle.neighbors.kneighbors(matrix, n_neighbors=requested)
    return pd.DataFrame(
        {
            "track_id": bundle.track_ids[indices[0]],
            "cosine_similarity": 1.0 - distances[0],
        }
    )
