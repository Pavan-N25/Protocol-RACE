"""A small mock model class used as a fallback for the scored detector.

Placing this class in a package module makes pickling/unpickling robust.
"""
from typing import Iterable


class MockModel:
    """Mock model with a predict_proba method.

    Returns probability proportional to mean of features.
    """

    def predict_proba(self, X: Iterable[Iterable[float]]):
        out = []
        for row in X:
            vals = list(row)
            s = sum(vals) / len(vals) if len(vals) else 0.0
            out.append([1.0 - s, s])
        return out
