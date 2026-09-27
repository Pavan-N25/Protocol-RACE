"""Scored detector with heuristic features and optional ML model.

This module provides a simple feature extractor and scoring function. If a
scikit-learn model file `model.pkl` exists in the project root, the
`ScoredDetector` will attempt to load it and use it for predictions. Otherwise
it falls back to a weighted heuristic score.
"""
from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass
from typing import Dict, Optional
import math


@dataclass
class ScoredDetector:
    name: str = "scored_detector"
    model_path: Optional[str] = None
    weights: Dict[str, float] = None

    def __post_init__(self):
        if self.weights is None:
            # default heuristic weights for features
            self.weights = {"injection_keyword": 2.0, "sensitive_mention": 1.5, "jailbreak_word": 2.5}
        self.model = None
        if self.model_path is None:
            candidate = os.path.join(os.getcwd(), "model.pkl")
            if os.path.exists(candidate):
                self.model_path = candidate
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as fh:
                    self.model = pickle.load(fh)
            except Exception:
                self.model = None

    def extract_features(self, text: str) -> Dict[str, float]:
        # expanded features
        feats = {
            "injection_keyword": 1.0 if re.search(r"ignore (previous )?instructions|disregard|bypass (safety|filter)", text, re.I) else 0.0,
            "sensitive_mention": 1.0 if re.search(r"password|api[_\-\s]?key|secret|ssn|social security", text, re.I) else 0.0,
            "jailbreak_word": 1.0 if re.search(r"jailbreak|help me hack|help me break", text, re.I) else 0.0,
            "has_url": 1.0 if re.search(r"https?://", text, re.I) else 0.0,
            "has_command": 1.0 if re.search(r"rm\s+-rf|curl .*sh\s*\|\s*sh|nc\s+-e|netcat", text, re.I) else 0.0,
            "length_log": math.log1p(len(text)),
        }
        return feats

    def score(self, text: str) -> float:
        feats = self.extract_features(text)
        if self.model is not None:
            try:
                # Expect model has predict_proba-like interface
                X = [[feats[k] for k in sorted(feats.keys())]]
                proba = self.model.predict_proba(X)
                # return probability of positive class if available
                return float(proba[0][-1])
            except Exception:
                pass
        # fallback heuristic weighted score normalized
        score = 0.0
        total_w = 0.0
        for k, w in self.weights.items():
            total_w += w
            score += feats.get(k, 0.0) * w
        # normalize by log length to keep score comparable
        norm = math.log1p(sum(abs(w) for w in self.weights.values()))
        return (score / total_w if total_w > 0 else 0.0) / (norm if norm > 0 else 1.0)

    def evaluate(self, text: str, threshold: float = 0.5) -> Dict[str, float]:
        s = self.score(text)
        return {"name": self.name, "score": s, "suspicious": s >= threshold}
