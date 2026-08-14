"""Regression tests for the hard 13-feature implementation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.features import (  # noqa: E402
    CANDIDATE_ENGINEERED_FEATURES,
    CLUSTER_FEATURES,
    EXPECTED_ENGINEERED_FEATURES,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
    RECOMMENDATION_FEATURES,
    FeatureBuilder,
    validate_engineered_features,
)


def sample_frame() -> pd.DataFrame:
    rows = []
    for index, year in enumerate([1998, 2004, 2012, 2018, 2020]):
        rows.append(
            {
                "duration_min": 2.5 + index * 0.4,
                "explicit": bool(index % 2),
                "release_year": year,
                "release_month": float(index + 1),
                "release_precision": "day",
                "danceability": 0.3 + index * 0.1,
                "energy": 0.4 + index * 0.08,
                "key": index,
                "loudness": -12.0 + index,
                "mode": index % 2,
                "speechiness": 0.04 + index * 0.01,
                "acousticness": 0.5 - index * 0.05,
                "instrumentalness": index * 0.02,
                "liveness": 0.1 + index * 0.02,
                "valence": 0.25 + index * 0.12,
                "tempo": 80.0 + index * 20.0,
                "time_signature": 4.0,
            }
        )
    return pd.DataFrame(rows)[RAW_INPUT_FEATURES]


class FeatureBuilderTest(unittest.TestCase):
    def test_all_expected_columns_are_real_and_valid(self):
        raw = sample_frame()
        builder = FeatureBuilder().fit(raw.iloc[:4])
        transformed = builder.transform(raw)
        self.assertEqual(transformed.columns.tolist(), MODEL_FEATURES)
        self.assertGreaterEqual(len(EXPECTED_ENGINEERED_FEATURES), 12)
        self.assertTrue(validate_engineered_features(transformed)["Status"].eq("PASS").all())

    def test_all_candidates_are_executable_before_selection(self):
        raw = sample_frame()
        candidates = FeatureBuilder().fit(raw.iloc[:4]).transform_candidates(raw)
        self.assertTrue(set(CANDIDATE_ENGINEERED_FEATURES).issubset(candidates.columns))
        self.assertGreater(len(CANDIDATE_ENGINEERED_FEATURES), len(EXPECTED_ENGINEERED_FEATURES))

    def test_secondary_contracts_exclude_target_and_time(self):
        forbidden = {"target_popularity", "release_year", "release_month", "decade"}
        self.assertFalse(forbidden.intersection(CLUSTER_FEATURES))
        self.assertFalse(forbidden.intersection(RECOMMENDATION_FEATURES))

    def test_test_values_cannot_change_learned_train_statistics(self):
        raw = sample_frame()
        builder = FeatureBuilder().fit(raw.iloc[:4])
        before = builder.get_learned_statistics()
        changed_test = raw.iloc[[4]].copy()
        changed_test["energy"] = 0.0
        changed_test["danceability"] = 0.0
        builder.transform(changed_test)
        self.assertEqual(before, builder.get_learned_statistics())


class DeploymentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline_path = ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib"
        if not cls.pipeline_path.exists():
            raise unittest.SkipTest("Run Notebook 06 first.")
        api_path = ROOT / "5.UNG_DUNG" / "5.1.backend_api" / "api.py"
        spec = importlib.util.spec_from_file_location("hitradar_api_test", api_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.client = TestClient(module.app)

    def test_health_and_prediction(self):
        raw = sample_frame().iloc[-1].to_dict()
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ready")
        response = self.client.post("/predict", json=raw)
        self.assertEqual(response.status_code, 200, response.text)

        pipeline = joblib.load(self.pipeline_path)
        expected = float(np.clip(pipeline.predict(pd.DataFrame([raw])[RAW_INPUT_FEATURES])[0], 0, 100))
        self.assertAlmostEqual(response.json()["predicted_popularity"], expected, places=3)

        cluster = self.client.post("/cluster", json=raw)
        self.assertEqual(cluster.status_code, 200, cluster.text)
        self.assertIsInstance(cluster.json()["cluster"], int)

    def test_recommendation_excludes_query_track(self):
        recommender_path = ROOT / "4.MODELS" / "hitradar_secondary" / "content_recommender.joblib"
        if not recommender_path.exists():
            raise unittest.SkipTest("Run Notebook 05 first.")
        bundle = joblib.load(recommender_path)
        query_id = str(bundle.track_ids[0])
        response = self.client.get(f"/recommend/{query_id}?n=5")
        self.assertEqual(response.status_code, 200, response.text)
        returned = {row["track_id"] for row in response.json()["recommendations"]}
        self.assertNotIn(query_id, returned)

    def test_raw_schema_rejects_engineered_input(self):
        raw = sample_frame().iloc[-1].to_dict()
        raw["dance_energy"] = 0.5
        self.assertEqual(self.client.post("/predict", json=raw).status_code, 422)

    def test_streamlit_initial_render(self):
        streamlit_path = ROOT / "5.UNG_DUNG" / "5.2.frontend" / "streamlit_app.py"
        app_test = AppTest.from_file(str(streamlit_path)).run(timeout=30)
        self.assertFalse(app_test.exception)
        self.assertEqual(
            [tab.label for tab in app_test.tabs],
            ["Overview", "Popularity Prediction", "Song Clustering", "Similar Songs"],
        )


if __name__ == "__main__":
    unittest.main()
