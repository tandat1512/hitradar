import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class TrainOnlyOutlierClipper(BaseEstimator, TransformerMixin):
    def __init__(self, columns, method='iqr', factor=1.5):
        self.columns = columns
        self.method = method
        self.factor = factor
        self.thresholds_ = {}
        self._is_fitted = False

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X
        for col in self.columns:
            if self.method == 'iqr':
                q1 = X_df[col].quantile(0.25)
                q3 = X_df[col].quantile(0.75)
                iqr = q3 - q1
                self.thresholds_[col] = (q1 - self.factor * iqr, q3 + self.factor * iqr)
        self._is_fitted = True
        self.n_features_in_ = X.shape[1]
        if hasattr(X, 'columns'):
            self.feature_names_in_ = X.columns.to_numpy()
        return self

    def transform(self, X):
        if not self._is_fitted:
            raise RuntimeError("Transformer not fitted.")
        X_out = X.copy()
        if isinstance(X_out, pd.DataFrame):
            for col in self.columns:
                lower, upper = self.thresholds_[col]
                X_out[col] = X_out[col].clip(lower=lower, upper=upper)
        else:
            for i, col in enumerate(self.columns):
                # if X is numpy array, assume self.columns refers to indices
                lower, upper = self.thresholds_[col]
                if isinstance(col, int):
                    X_out[:, col] = np.clip(X_out[:, col], lower, upper)
        return X_out

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return input_features
        if hasattr(self, 'feature_names_in_'):
            return self.feature_names_in_
        return np.array(self.columns)


class ExplicitMissingImputer(BaseEstimator, TransformerMixin):
    def __init__(self, fill_value='__MISSING__'):
        self.fill_value = fill_value

    def fit(self, X, y=None):
        self._is_fitted = True
        return self

    def transform(self, X):
        if not self._is_fitted:
            raise RuntimeError("Transformer not fitted.")
        X_out = X.copy()
        if isinstance(X_out, pd.DataFrame):
            return X_out.fillna(self.fill_value).astype(str)
        else:
            # Assume it is string array
            mask = pd.isna(X_out)
            X_out = X_out.astype(str)
            X_out[mask] = self.fill_value
            return X_out

    def get_feature_names_out(self, input_features=None):
        return input_features

class ExplicitMissingIndicator(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        self._is_fitted = True
        return self

    def transform(self, X):
        if not self._is_fitted:
            raise RuntimeError("Transformer not fitted.")
        if isinstance(X, pd.DataFrame):
            X_out = X[self.columns].isna().astype(int)
        else:
            X_out = pd.isna(X).astype(int)
        return X_out

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return np.array([f"{f}_missing" for f in input_features])
        return np.array([f"{f}_missing" for f in self.columns])
