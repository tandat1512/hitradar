# ScaledOneHotEncoder Explanation

**Feature 2.2 — Leakage-Safe Preprocessing Pipeline**
**Component Documentation**
**Generated**: 2026-07-17

---

## 1. Class Definition

```python
class ScaledOneHotEncoder(BaseEstimator, TransformerMixin):
    """
    OneHotEncoder wrapper that outputs float32 and handles unknown categories.
    """
    
    def __init__(self, categories="auto", handle_unknown="ignore", sparse_output=False):
        self.categories = categories
        self.handle_unknown = handle_unknown
        self.sparse_output = sparse_output
        self._encoder = OneHotEncoder(
            categories=categories,
            handle_unknown=handle_unknown,
            sparse_output=sparse_output,
            dtype=np.float32,  # Key: forces float32 output
        )
```

---

## 2. Purpose

The `ScaledOneHotEncoder` is a thin wrapper around scikit-learn's `OneHotEncoder` with the following modifications:

| Feature | Standard OneHotEncoder | ScaledOneHotEncoder |
|---|---|---|
| Output dtype | float64 (default) | **float32** (hardcoded) |
| Unknown handling | error/ignore | **ignore** (hardcoded) |
| Sparse output | True (default) | **False** (hardcoded) |

### Why float32?

- **Memory efficiency**: 50% reduction in memory vs float64
- **Ridge solver compatibility**: Works with both dense and sparse formats
- **Sufficient precision**: float32 provides ~7 digits of precision, more than enough for model coefficients

---

## 3. API Surface

| Method | Description |
|---|---|
| `fit(X, y=None)` | Fits the internal OneHotEncoder |
| `transform(X)` | Transforms categorical features to one-hot encoded arrays |
| `get_feature_names_out(input_features)` | Returns output feature names |

---

## 4. Wrapped Encoder Access

The internal encoder is accessible via `_encoder` attribute:

```python
# Access categories after fit
encoder = preprocessor.named_transformers_['encoder']._encoder
categories = encoder.categories_
feature_names = encoder.feature_names_in_
```

---

## 5. Leakage Considerations

The `ScaledOneHotEncoder` itself does not introduce leakage. However:

1. **Categories must be fitted on train only**: The encoder's `categories_` attribute is set during `fit()` on the training data only.
2. **Unknown categories**: `handle_unknown="ignore"` ensures that validation/test categories not seen in training are handled gracefully (all zeros).
3. **No target leakage**: The encoder does not use `y` during fitting.

---

## 6. Output Schema (Ridge)

When applied to the HitRadar dataset, the encoder produces:

| Input Feature | Categories | Output Columns |
|---|---|---|
| release_month | 1-12 + nan | 13 |
| decade | 1900-2000 (10 values) | 10 |
| release_precision | day/month/year | 3 |
| key | 0-11 | 12 |
| time_signature | 1,3,4,5 + nan | 5 |

**Total OHE output**: 43 columns (before scaling)

---

## 7. Integration with ColumnTransformer

The `ScaledOneHotEncoder` is used within a `ColumnTransformer` in the Ridge preprocessor:

```python
('encoder', ScaledOneHotEncoder(), categorical_cols)
```

The numeric pipeline handles scaling separately:

```python
('scaler', StandardScaler(), numeric_cols)
```

This separation ensures that:
- Categorical features are one-hot encoded
- Numeric features are standardized
- Both transformations use train-only statistics

---

**Documentation Complete**
