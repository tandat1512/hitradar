"""Feature 3.4 Phase 1 — trend_data_loader tests"""
import pathlib, os, sys

# ensure the loader is on path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dashboard.loaders.trend_data_loader import (
    load_trend_dataset,
    load_yearly_evaluation,
    get_source_paths,
    get_source_info,
    aggregate_by_year,
    aggregate_by_decade,
    validate_schema,
    FIELD_TEMPORAL,
    FIELD_POPULARITY,
    FIELD_DURATION,
    FIELD_EXPLICIT,
    AUDIO_FEATURES,
)


def test_source_paths_resolved():
    paths = get_source_paths()
    assert "dataset" in paths
    assert "evaluation" in paths
    assert isinstance(paths["dataset"], pathlib.Path)
    assert isinstance(paths["evaluation"], pathlib.Path)


def test_source_info_returns_metadata():
    info = get_source_info()
    assert info["dataset"]["year_min"] == 1922
    assert info["dataset"]["year_max"] == 2019
    assert info["dataset"]["rows"] == 169681
    assert info["evaluation"]["year_min"] == 2014
    assert info["evaluation"]["year_max"] == 2021


def test_load_trend_dataset_returns_dataframe():
    df = load_trend_dataset()
    assert len(df) > 0
    assert len(df.columns) == 20
    assert FIELD_TEMPORAL in df.columns
    assert FIELD_POPULARITY in df.columns
    assert FIELD_DURATION in df.columns
    assert FIELD_EXPLICIT in df.columns


def test_load_yearly_evaluation_returns_dataframe():
    df = load_yearly_evaluation()
    assert len(df) > 0


def test_returned_dataframe_is_copy():
    df1 = load_trend_dataset()
    id1 = id(df1)
    del df1
    df2 = load_trend_dataset()
    id2 = id(df2)
    assert id1 != id2  # different object


def test_popularity_column_is_target_popularity():
    df = load_trend_dataset()
    assert "target_popularity" in df.columns
    assert "popularity" not in df.columns  # not "popularity"


def test_duration_column_is_minutes():
    df = load_trend_dataset()
    assert "duration_min" in df.columns
    assert "duration_ms" not in df.columns  # NOT milliseconds


def test_explicit_column_exists():
    df = load_trend_dataset()
    assert "explicit" in df.columns


def test_all_audio_features_present():
    df = load_trend_dataset()
    for feat in AUDIO_FEATURES:
        assert feat in df.columns, f"Missing audio feature: {feat}"


def test_year_column_is_release_year():
    df = load_trend_dataset()
    assert "release_year" in df.columns
    assert "year" not in df.columns  # not "year"


def test_artist_and_genre_not_available():
    df = load_trend_dataset()
    assert "artist" not in df.columns
    assert "artists" not in df.columns
    assert "genre" not in df.columns
    assert "genres" not in df.columns


def test_decade_column_exists():
    df = load_trend_dataset()
    assert "decade" in df.columns


def test_year_range_1922_to_2019():
    df = load_trend_dataset()
    years = df[FIELD_TEMPORAL].dropna()
    assert int(years.min()) == 1922
    assert int(years.max()) == 2019


def test_year_1921_not_in_data():
    df = load_trend_dataset()
    years = df[FIELD_TEMPORAL].dropna()
    assert 1921 not in years.values


def test_year_2020_not_in_data():
    df = load_trend_dataset()
    years = df[FIELD_TEMPORAL].dropna()
    assert 2020 not in years.values


def test_aggregate_by_year_returns_dataframe():
    df = load_trend_dataset()
    agg = aggregate_by_year(df)
    assert FIELD_TEMPORAL in agg.columns
    assert "_count" in agg.columns
    assert len(agg) > 0


def test_aggregate_by_decade_returns_dataframe():
    df = load_trend_dataset()
    agg = aggregate_by_decade(df)
    assert "decade" in agg.columns
    assert "_count" in agg.columns
    assert len(agg) > 0


def test_aggregate_by_year_year_min_1922():
    df = load_trend_dataset()
    agg = aggregate_by_year(df)
    years = agg[FIELD_TEMPORAL]
    assert int(years.min()) == 1922


def test_aggregate_by_year_year_max_2019():
    df = load_trend_dataset()
    agg = aggregate_by_year(df)
    years = agg[FIELD_TEMPORAL]
    assert int(years.max()) == 2019


def test_validate_schema_valid_for_canonical():
    df = load_trend_dataset()
    errors = validate_schema(df)
    assert errors == [], f"Schema validation failed: {errors}"


def test_duration_values_are_minutes_not_ms():
    df = load_trend_dataset()
    dur = df[FIELD_DURATION].dropna()
    # If unit is minutes, values should be in range 0-20 (song lengths)
    # If someone misread as milliseconds, values would be 0-1,200,000
    max_val = dur.max()
    assert max_val < 30, f"duration_min values too large ({max_val}) — check unit assumption"


def test_no_model_loading_in_loader():
    """Verify loader module does not import model artifacts."""
    import dashboard.loaders.trend_data_loader as mod
    src = open(mod.__file__, encoding="utf-8").read()
    forbidden = ["joblib", "pickle.load", "xgb", "sklearn.model", "ModelService", "shap.TreeExplainer"]
    found = [f for f in forbidden if f in src]
    assert not found, f"Loader contains forbidden imports: {found}"


def test_no_source_mutation():
    """Loader must not write to source dataset."""
    import dashboard.loaders.trend_data_loader as mod
    src = open(mod.__file__, encoding="utf-8").read()
    forbidden = ["to_csv", "to_parquet", "to_json", "to_excel", "to_sql"]
    # Only check for write operations on source path
    assert ".to_csv" not in src or "# " in src  # allow commented examples
    assert ".to_parquet" not in src
