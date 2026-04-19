"""
term_audit/falsification.py

Falsifiable-prediction and boundary-condition machinery.

Implements preempts #1 (demand falsifiability at every step) and #6
(document every assumption as a boundary condition) from
docs/PREEMPTING_ATTACKS.md.

A claim about framework behavior must be expressible as: under
conditions C, the framework predicts observation O. If O is not
observed, the claim is falsified. Claims that cannot be cast in this
form are not arguments — they are rhetoric, and the framework refuses
to engage with them as if they were arguments.

A boundary condition documents the regime in which a model is valid.
The point is not "this might be wrong" — it is "this is valid in
regime X and breaks at boundary Y." When the current measurement
system silently assumes the boundary doesn't exist, that is the
attack vector to surface.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# BoundaryCondition
# ---------------------------------------------------------------------------

@dataclass
class BoundaryCondition:
    """A regime within which a model holds, and the conditions that
    invalidate it.

    `valid_when` and `breaks_when` are predicates expressed in prose;
    a future verification layer (PhysicsGuard or equivalent) can check
    them automatically. For now they document the regime explicitly so
    a critic must declare which regime they are arguing about.
    """
    regime_description: str
    valid_when: List[str]
    breaks_when: List[str]
    breakdown_signal: str               # observable that signals breakdown
    source_refs: List[str] = field(default_factory=list)

    def is_documented(self) -> bool:
        """True iff regime, valid_when, breaks_when, and breakdown_signal
        are all non-empty. A boundary that doesn't say where it breaks
        isn't a boundary."""
        return bool(
            self.regime_description.strip()
            and self.valid_when
            and self.breaks_when
            and self.breakdown_signal.strip()
        )


# ---------------------------------------------------------------------------
# FalsifiablePrediction
# ---------------------------------------------------------------------------

PREDICTION_STATUS_VALUES = {"untested", "supported", "falsified", "ambiguous"}


@dataclass
class FalsifiablePrediction:
    """A specific, testable prediction the framework makes.

    `predicted_observation` and `falsification_test` are the load-bearing
    fields. If a critic disputes the claim, they run the falsification
    test under the stated conditions; the result is binary (the
    prediction held or it didn't). Argument substitutes for testing
    only when one of these fields is missing — at which point the
    claim is not a prediction.
    """
    claim: str
    conditions: List[str]               # under what regime/setup
    predicted_observation: str
    falsification_test: str             # procedure to run
    source_refs: List[str] = field(default_factory=list)
    last_run_result: str = "untested"   # one of PREDICTION_STATUS_VALUES
    last_run_date: str = ""             # free-form ISO date if available
    last_run_notes: str = ""

    def __post_init__(self):
        if self.last_run_result not in PREDICTION_STATUS_VALUES:
            raise ValueError(
                f"unknown prediction status: {self.last_run_result!r}. "
                f"valid: {sorted(PREDICTION_STATUS_VALUES)}"
            )

    def is_falsifiable(self) -> bool:
        """True iff the prediction has all three load-bearing fields:
        a predicted observation, a falsification test, and at least
        one stated condition."""
        return bool(
            self.predicted_observation.strip()
            and self.falsification_test.strip()
            and self.conditions
        )


# ---------------------------------------------------------------------------
# PredictionRegistry
# ---------------------------------------------------------------------------

@dataclass
class PredictionRegistry:
    """A registry of falsifiable predictions across modules.

    Modules register predictions at import time or via explicit
    `register()` call. The registry surfaces:
      - which predictions exist (so a critic can see what could be
        tested)
      - which predictions have been tested and with what result
      - which predictions are not yet falsifiable (missing test or
        condition spec) — the framework's own audit-of-itself
    """
    predictions: List[FalsifiablePrediction] = field(default_factory=list)

    def register(self, prediction: FalsifiablePrediction) -> None:
        self.predictions.append(prediction)

    def by_status(self, status: str) -> List[FalsifiablePrediction]:
        if status not in PREDICTION_STATUS_VALUES:
            raise ValueError(
                f"unknown status {status!r}; valid {sorted(PREDICTION_STATUS_VALUES)}"
            )
        return [p for p in self.predictions if p.last_run_result == status]

    def unfalsifiable(self) -> List[FalsifiablePrediction]:
        """Predictions missing the load-bearing fields. These are the
        framework's own scaffold-vs-production gap — cleaner to surface
        than to hide."""
        return [p for p in self.predictions if not p.is_falsifiable()]

    def summary(self) -> Dict[str, int]:
        out: Dict[str, int] = {s: 0 for s in PREDICTION_STATUS_VALUES}
        out["unfalsifiable"] = 0
        for p in self.predictions:
            if not p.is_falsifiable():
                out["unfalsifiable"] += 1
            out[p.last_run_result] += 1
        out["total"] = len(self.predictions)
        return out
