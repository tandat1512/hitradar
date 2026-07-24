from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np


class IQRClipper(BaseEstimator, TransformerMixin):
    """Clip outliers using IQR method fitted on training data."""

    def __init__(self, q1=0.25, q3=0.75, multiplier=1.5, columns=None):
        self.q1 = q1
        self.q3 = q3
        self.multiplier = multiplier
        self.columns = columns
        self.lower_ = None
        self.upper_ = None
        self.iqr_ = None

    def fit(self, X, y=None):
        """Fit the clipper on training data."""
        self.lower_ = np.nanpercentile(X, self.q1 * 100, axis=0)
        self.upper_ = np.nanpercentile(X, self.q3 * 100, axis=0)
        self.iqr_ = self.upper_ - self.lower_
        return self

    def transform(self, X):
        """Transform by clipping outliers."""
        X_copy = X.copy()
        for i in range(X.shape[1]):
            if self.lower_ is not None and i < len(self.lower_):
                lower = self.lower_[i] - self.multiplier * self.iqr_[i]
                upper = self.upper_[i] + self.multiplier * self.iqr_[i]
                X_copy[:, i] = np.clip(X_copy[:, i], lower, upper)
        return X_copy
