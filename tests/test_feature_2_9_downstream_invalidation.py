"""
Tests for downstream stage invalidation based on actual registry dependencies.
Feature 2.9 Phase 2 — test_feature_2_9_downstream_invalidation.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.orchestrator import get_downstream_stages


REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation",
    "registries", "epic2_pipeline_stage_registry.json"
)


@pytest.fixture
def stage_registry():
    import json
    with open(REGISTRY_PATH) as f:
        return json.load(f)


class TestDownstreamInvalidation:
    """Stale checkpoint invalidates all downstream stages via dependency graph."""

    def test_p50_downstream_is_list(self, stage_registry):
        """get_downstream_stages returns a list."""
        result = get_downstream_stages("P50_TRAIN_CANDIDATES", stage_registry)
        assert isinstance(result, list)

    def test_p50_invalidates_p60(self, stage_registry):
        """P50 stale → P60_VALIDATE_AND_SELECT_CHAMPION is also stale."""
        downstream = get_downstream_stages("P50_TRAIN_CANDIDATES", stage_registry)
        assert "P60_VALIDATE_AND_SELECT_CHAMPION" in downstream

    def test_p60_invalidates_p65(self, stage_registry):
        """P60 stale → P65_LOCK_CHAMPION is also stale."""
        downstream = get_downstream_stages("P60_VALIDATE_AND_SELECT_CHAMPION", stage_registry)
        assert "P65_LOCK_CHAMPION" in downstream

    def test_p65_invalidates_p70(self, stage_registry):
        """P65 stale → P70_FINAL_TEST is also stale."""
        downstream = get_downstream_stages("P65_LOCK_CHAMPION", stage_registry)
        assert "P70_FINAL_TEST" in downstream

    def test_p65_invalidates_p80(self, stage_registry):
        """P65 stale → P80_EXPLAINABILITY is also stale."""
        downstream = get_downstream_stages("P65_LOCK_CHAMPION", stage_registry)
        assert "P80_EXPLAINABILITY" in downstream

    def test_p65_invalidates_p90(self, stage_registry):
        """P65 stale → P90_PACKAGING is also stale."""
        downstream = get_downstream_stages("P65_LOCK_CHAMPION", stage_registry)
        assert "P90_PACKAGING" in downstream

    def test_p30_invalidates_p40(self, stage_registry):
        """P30 stale → P40_FEATURE_ENGINEERING is also stale."""
        downstream = get_downstream_stages("P30_PREPROCESSING", stage_registry)
        assert "P40_FEATURE_ENGINEERING" in downstream

    def test_p40_invalidates_p50(self, stage_registry):
        """P40 stale → P50_TRAIN_CANDIDATES is also stale."""
        downstream = get_downstream_stages("P40_FEATURE_ENGINEERING", stage_registry)
        assert "P50_TRAIN_CANDIDATES" in downstream

    def test_p00_invalidates_p10(self, stage_registry):
        """P00 stale → P10 is also stale."""
        downstream = get_downstream_stages("P00_PREFLIGHT", stage_registry)
        assert "P10_VALIDATE_DATASET" in downstream

    def test_p00_invalidates_p98(self, stage_registry):
        """P00 stale → P98_MONITORING is also stale."""
        downstream = get_downstream_stages("P00_PREFLIGHT", stage_registry)
        assert "P98_MONITORING" in downstream

    def test_p10_invalidates_p20(self, stage_registry):
        """P10 stale → P20_TEMPORAL_SPLIT is also stale."""
        downstream = get_downstream_stages("P10_VALIDATE_DATASET", stage_registry)
        assert "P20_TEMPORAL_SPLIT" in downstream

    def test_p70_has_no_downstream(self, stage_registry):
        """P70_FINAL_TEST has no downstream stages."""
        downstream = get_downstream_stages("P70_FINAL_TEST", stage_registry)
        assert downstream == []

    def test_p80_has_no_downstream(self, stage_registry):
        """P80_EXPLAINABILITY has no downstream stages."""
        downstream = get_downstream_stages("P80_EXPLAINABILITY", stage_registry)
        assert downstream == []

    def test_p90_has_no_downstream(self, stage_registry):
        """P90_PACKAGING has no downstream stages."""
        downstream = get_downstream_stages("P90_PACKAGING", stage_registry)
        assert downstream == []

    def test_p98_has_no_downstream(self, stage_registry):
        """P98_MONITORING has no downstream stages."""
        downstream = get_downstream_stages("P98_MONITORING", stage_registry)
        assert downstream == []

    def test_p99_has_no_downstream(self, stage_registry):
        """P99_RUN_SUMMARY has no downstream stages."""
        downstream = get_downstream_stages("P99_RUN_SUMMARY", stage_registry)
        assert downstream == []

    def test_downstream_is_deterministic(self, stage_registry):
        """Same input always returns same downstream list."""
        r1 = get_downstream_stages("P50_TRAIN_CANDIDATES", stage_registry)
        r2 = get_downstream_stages("P50_TRAIN_CANDIDATES", stage_registry)
        assert r1 == r2

    def test_empty_registry_returns_empty(self):
        """Empty registry returns empty downstream."""
        result = get_downstream_stages("P00", [])
        assert result == []
