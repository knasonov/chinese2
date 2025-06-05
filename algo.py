# Granular word-recall predictor with online logistic regression.
# Author: 2025-06-05

from __future__ import annotations

import math
import random
import collections
from typing import DefaultDict, Dict, List, Optional


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------

def cosine(u: List[float], v: List[float]) -> float:
    """Return cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return 0.0 if nu == 0.0 or nv == 0.0 else dot / (nu * nv)


# ----------------------------------------------------------------------
# Predictor
# ----------------------------------------------------------------------

class WordPredictor:
    """Estimate recall probability for a single word."""

    # ---------- hyper-parameters ----------
    DEFAULT_LAMBDA: Dict[str, float] = {
        "reading": 1 / (60 * 60 * 12),   # half-life ≈ 12 h
        "flashcard": 1 / (60 * 60 * 24 * 3),  # half-life ≈ 3 days
        "quiz": 1 / (60 * 60 * 24 * 7),       # half-life ≈ 1 week
    }
    LEARNING_RATE: float = 0.05
    # -------------------------------------

    def __init__(self,
                 modes: Optional[List[str]] = None,
                 lambdas: Optional[Dict[str, float]] = None) -> None:
        self.modes = modes if modes else ["reading", "flashcard", "quiz"]
        self.lambda_: Dict[str, float] = dict(self.DEFAULT_LAMBDA)
        if lambdas:
            self.lambda_.update(lambdas)

        # decayed tallies S and F per mode
        self.S: DefaultDict[str, float] = collections.defaultdict(float)
        self.F: DefaultDict[str, float] = collections.defaultdict(float)

        # logistic coefficients and bias
        self.theta_S: Dict[str, float] = {m: 0.80 for m in self.modes}
        self.theta_F: Dict[str, float] = {m: 0.80 for m in self.modes}
        self.theta_0: float = -1.5

        # last-updated timestamp for decay bookkeeping
        self.last_update_ts: float = 0.0

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def probability(self, now_ts: float, cur_ctx: Optional[List[float]] = None) -> float:
        """Return probability of recall at time *now_ts*."""
        self._decay_to(now_ts)
        logit = self.theta_0
        for m in self.modes:
            logit += self.theta_S[m] * self.S[m] - self.theta_F[m] * self.F[m]
        return 1.0 / (1.0 + math.exp(-logit))

    def update(self,
               mode: str,
               outcome: int,
               event_ts: float,
               event_ctx: Optional[List[float]] = None,
               cur_ctx: Optional[List[float]] = None) -> None:
        """Record an interaction and update the model."""
        if mode not in self.modes:
            # unseen mode – initialize on the fly
            self.modes.append(mode)
            self.lambda_[mode] = self.lambda_.get(mode, 1 / (60 * 60 * 24))
            self.S[mode] = 0.0
            self.F[mode] = 0.0
            self.theta_S[mode] = 0.80
            self.theta_F[mode] = 0.80

        # 1) decay tallies up to event_ts
        self._decay_to(event_ts)

        # 2) similarity weighting for this event
        sim = 1.0
        if event_ctx is not None and cur_ctx is not None:
            sim = cosine(event_ctx, cur_ctx)
        if outcome == 1:
            self.S[mode] += sim
        else:
            self.F[mode] += sim

        # 3) prediction before update
        p = self._logistic_raw()

        # 4) stochastic gradient descent step
        error = outcome - p
        lr = self.LEARNING_RATE

        self.theta_0 += lr * error
        for m in self.modes:
            self.theta_S[m] += lr * error * self.S[m]
            self.theta_F[m] -= lr * error * self.F[m]

    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------

    def _decay_to(self, new_ts: float) -> None:
        """Exponentially decay tallies up to *new_ts*."""
        dt = new_ts - self.last_update_ts
        if dt <= 0:
            return
        for m in self.modes:
            factor = math.exp(-self.lambda_[m] * dt)
            self.S[m] *= factor
            self.F[m] *= factor
        self.last_update_ts = new_ts

    def _logistic_raw(self) -> float:
        """Compute recall probability without further decay."""
        logit = self.theta_0
        for m in self.modes:
            logit += self.theta_S[m] * self.S[m] - self.theta_F[m] * self.F[m]
        return 1.0 / (1.0 + math.exp(-logit))

    # ----------------------------------------------------------
    # Convenience: simulate a recall attempt
    # ----------------------------------------------------------

    def recall(self, now_ts: float, cur_ctx: Optional[List[float]] = None) -> bool:
        """Return True iff a simulated recall succeeds."""
        return random.random() < self.probability(now_ts, cur_ctx)


# ----------------------------------------------------------------------
# Stand-alone demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    import time

    now = time.time()
    wp = WordPredictor()

    # day 0: reading success
    wp.update("reading", 1, now)

    # 8h later: reading failure
    eight_h = 60 * 60 * 8
    wp.update("reading", 0, now + eight_h)

    # flashcard drill 24h later: success
    wp.update("flashcard", 1, now + 24 * 3600)

    # prediction 5 days later
    prob = wp.probability(now + 5 * 24 * 3600)
    print(f"Recall probability after 5 days: {prob:.3f}")
