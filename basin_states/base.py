"""
basin_states/base.py

Base class for any basin a firm depends on. A basin has:
  - current state (scalar or vector)
  - capacity (what the basin can sustainably provide)
  - trajectory (rate of change, positive = regenerating, negative = depleting)
  - cliff thresholds (state values below which cascade failure triggers)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BasinState:
    name: str
    basin_type: str = ""              # normalized type identifier
                                       # ("soil", "air", "water", "biology", ...)
    state: Dict[str, float] = field(default_factory=dict)
    capacity: Dict[str, float] = field(default_factory=dict)
    trajectory: Dict[str, float] = field(default_factory=dict)
    cliff_thresholds: Dict[str, float] = field(default_factory=dict)
    # metrics where HIGH values are BAD. Declarative per-basin instead
    # of a global hardcoded set in the cascade detector.
    high_is_bad: set = field(default_factory=set)
    last_updated: Optional[str] = None
    notes: str = ""

    def fraction_remaining(self, key: str) -> float:
        """State as fraction of capacity. 1.0 = full, 0.0 = depleted."""
        cap = self.capacity.get(key)
        if cap is None or cap == 0:
            return float("nan")
        return self.state.get(key, 0.0) / cap

    def time_to_cliff(self, key: str) -> Optional[float]:
        """Time (in trajectory units) until state crosses cliff threshold.
        Returns None if not trending toward cliff."""
        s = self.state.get(key)
        t = self.trajectory.get(key)
        c = self.cliff_thresholds.get(key)
        if s is None or t is None or c is None:
            return None
        if t >= 0:
            return None  # regenerating or stable, no cliff
        if s <= c:
            return 0.0  # already past cliff
        return (s - c) / abs(t)

    def is_degrading(self) -> List[str]:
        """Return keys with negative trajectory."""
        return [k for k, v in self.trajectory.items() if v < 0]
