"""
distributional/signal_asymmetry.py

Interface stub for cross-observer signal-asymmetry reporting.

Per `Todo.md` priority 2, the production distributional analysis
lives in the sister repo
`thermodynamic-accountability-framework/money_distribution/` and
`investment_distribution/`. This module is deliberately a lean stub
— not an implementation — providing:

  - A shared data shape (`ObserverAsymmetryReport`) the sister-repo
    implementation can target.
  - A literature-anchor registry documenting the mature empirical
    traditions the analysis should be grounded in.
  - A minimal helper (`observer_delta`) that computes the simplest
    possible asymmetry diagnostic — the gap between two observers'
    money-signal quality under the same regime.

The literature anchors are four well-studied strands identified in
AUDIT_14 § A.3:

  - **Distributional National Accounts** (Piketty-Saez-Zucman,
    WID.world): decomposes aggregate national accounts by percentile.
    The "same aggregate, different observer" premise in structured,
    open-data form.
  - **Heterogeneous Agent New Keynesian (HANK)** macro (Kaplan-Moll-
    Violante): central-bank models that explicitly track different
    monetary-policy outcomes across the wealth distribution.
    `money_signal/coupling_observer.py` is already HANK-shaped.
  - **Stratification economics** (Darity-Hamilton): treats group
    position as the analytic primitive. Matches the framework's
    discrete `ObserverPosition` enum better than continuous-
    percentile approaches.
  - **Fiscal incidence analysis** (Harberger / CBO / JCT): statutory
    vs economic incidence — who nominally pays vs who actually
    bears the cost.

Not an implementation. Not a gate. Not consumed by the rest of the
framework today. If you need full cross-observer analysis, go to
the sister repo.

AUDIT_14 Part C, AUDIT_15 companion. CC0. Stdlib-only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from term_audit.provenance import Provenance, empirical, theoretical


# ---------------------------------------------------------------------------
# Literature anchor registry
# ---------------------------------------------------------------------------

LITERATURE_ANCHORS: Dict[str, Provenance] = {
    "distributional_national_accounts": empirical(
        source_refs=[
            "Piketty, Saez & Zucman 2018, 'Distributional National "
            "Accounts: Methods and Estimates for the United States', "
            "QJE 133(2)",
            "Alvaredo, Chancel, Piketty, Saez, Zucman 2020 "
            "(World Inequality Database / WID.world)",
        ],
        rationale=(
            "DNA decomposes aggregate national accounts by percentile "
            "of the distribution; directly implements the 'same "
            "aggregate, different observer' premise the signal-"
            "asymmetry module needs. Open cross-country decadal "
            "datasets."
        ),
        scope_caveat=(
            "DNA uses continuous percentile framing; the framework's "
            "ObserverPosition enum is discrete. A bridge layer is "
            "required."
        ),
        falsification_test=(
            "compare DNA decomposition against the observer-position "
            "coupling K values from money_signal/coupling_observer.py "
            "on matched case studies; mismatches surface where the "
            "discrete enum misrepresents continuous distribution"
        ),
    ),

    "heterogeneous_agent_macro": empirical(
        source_refs=[
            "Kaplan, Moll & Violante 2018, 'Monetary Policy According "
            "to HANK', AER 108(3)",
            "Bhandari, Evans, Golosov & Sargent 2021, 'Inequality, "
            "Business Cycles, and Monetary-Fiscal Policy', Econometrica 89",
        ],
        rationale=(
            "HANK models track different monetary-policy outcomes "
            "across the wealth distribution — directly parallel to "
            "the K-matrix observer dependency in "
            "money_signal/coupling_observer.py. Used at the Fed and "
            "ECB for policy analysis."
        ),
        falsification_test=(
            "take a documented monetary-policy shock (e.g., 2008 Fed "
            "LSAP); compute expected observer-differential response "
            "from coupling_observer.py; compare to HANK-model "
            "predictions on the same event"
        ),
    ),

    "stratification_economics": theoretical(
        rationale=(
            "Stratification economics (Darity, Hamilton, et al.) "
            "treats group position — not individuals — as the analytic "
            "primitive. Provides the methodological defense for the "
            "framework's discrete ObserverPosition enum rather than a "
            "continuous distribution. The claim that routing effects "
            "happen at the group level, not the percentile level, is "
            "structurally aligned with money_signal/coupling_observer.py."
        ),
        source_refs=[
            "Darity 2005, 'Stratification Economics: The Role of "
            "Intergroup Inequality', Journal of Economics and Finance 29(2)",
            "Darity, Hamilton et al. 2015, 'Stratification Economics: "
            "A General Theory of Intergroup Inequality', in Cramer & "
            "Hamilton eds., The Hidden Rules of Race",
        ],
        falsification_test=(
            "identify a coupling effect that operates at the individual "
            "percentile level and NOT at the group-position level; if "
            "found, the discrete-enum framing loses its theoretical "
            "basis"
        ),
    ),

    "fiscal_incidence": empirical(
        source_refs=[
            "Harberger 1962, 'The Incidence of the Corporation Income "
            "Tax', Journal of Political Economy 70(3)",
            "CBO 2020 onward, 'The Distribution of Household Income' "
            "(annual)",
            "Joint Committee on Taxation, 'Distributional Analysis' "
            "methodology (JCX-14-93 and successors)",
        ],
        rationale=(
            "Statutory-incidence-vs-economic-incidence distinction is "
            "directly reusable for the framework's 'formal bearer vs "
            "real bearer' question on cascade coupling risk. CBO and "
            "JCT publish annual distributional analyses with "
            "standardized methodology."
        ),
        scope_caveat=(
            "incidence analysis is mature for tax policy; applying it "
            "to monetary-signal coupling requires re-deriving the "
            "incidence model for a K-matrix rather than a price "
            "change"
        ),
        falsification_test=(
            "derive the incidence model for a K[N][R] shock under "
            "observer heterogeneity; compare to the Harberger-style "
            "static incidence predictions"
        ),
    ),
}


# ---------------------------------------------------------------------------
# Shared data shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObserverAsymmetryReport:
    """Shared data shape for cross-observer asymmetry analysis.

    Attributes are deliberately minimal — the sister repo's
    implementation is expected to attach richer telemetry. What this
    stub guarantees is that any such report carries at least these
    fields in these types, so downstream consumers can reason about
    the signal-asymmetry structure without coupling to the full
    sister-repo implementation.

    Fields:
      subject          short label for what's being compared
                       (e.g., "money_signal K[N][R] under STRESSED")
      observers        ordered list of observer labels; exactly 2
      values           per-observer scalar for the subject
      delta            values[1] - values[0]
      asymmetry_ratio  values[1] / values[0] where defined, else None
      caveats          free-form list of caveats (e.g., "same
                       regime, different observer position"); the
                       caller is responsible for filling these
      literature_anchor_key  which LITERATURE_ANCHORS entry grounds
                             this comparison; caller provides
    """
    subject: str
    observers: Tuple[str, str]
    values: Tuple[float, float]
    delta: float
    asymmetry_ratio: Optional[float]
    caveats: Tuple[str, ...] = ()
    literature_anchor_key: Optional[str] = None


# ---------------------------------------------------------------------------
# Minimal helper
# ---------------------------------------------------------------------------

def observer_delta(
    subject: str,
    observer_a: str,
    value_a: float,
    observer_b: str,
    value_b: float,
    *,
    caveats: Tuple[str, ...] = (),
    literature_anchor_key: Optional[str] = None,
) -> ObserverAsymmetryReport:
    """Build an ObserverAsymmetryReport from two scalar observer-
    indexed values.

    This is the simplest possible asymmetry diagnostic: subtract.
    The real work — choice of observer positions, scalar extraction
    from a K matrix, handling non-scalar outputs, weighting, etc. —
    belongs in the sister repo. This helper exists so that in-repo
    callers who just want to name an asymmetry have a structured
    output shape.
    """
    delta = value_b - value_a
    try:
        ratio: Optional[float] = value_b / value_a if value_a != 0.0 else None
    except ZeroDivisionError:
        ratio = None

    if literature_anchor_key is not None:
        if literature_anchor_key not in LITERATURE_ANCHORS:
            raise ValueError(
                f"unknown literature_anchor_key {literature_anchor_key!r}; "
                f"expected one of {sorted(LITERATURE_ANCHORS.keys())}"
            )

    return ObserverAsymmetryReport(
        subject=subject,
        observers=(observer_a, observer_b),
        values=(value_a, value_b),
        delta=delta,
        asymmetry_ratio=ratio,
        caveats=tuple(caveats),
        literature_anchor_key=literature_anchor_key,
    )


# ---------------------------------------------------------------------------
# Sister-repo pointer
# ---------------------------------------------------------------------------

SISTER_REPO_IMPLEMENTATION_NOTE = """
Full cross-observer analysis lives in:

  thermodynamic-accountability-framework/money_distribution/
  thermodynamic-accountability-framework/investment_distribution/

These repos consume `ObserverAsymmetryReport` (or its richer
descendant) and produce:

  - For any K-matrix context, who bears each coupling dimension?
  - Tracing extraction flows upstream — which actors set the
    terms that determined the current coupling?
  - Asymmetry scores between best-case and worst-case observer
    positions in the same regime.

The implementation there is grounded in the four literature
anchors registered in LITERATURE_ANCHORS above.

See docs/AUDIT_14.md § A.3 + docs/Todo.md priority 2.
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _demo() -> None:
    """Minimal demo: one toy observer-asymmetry report grounded in
    one literature anchor."""
    report = observer_delta(
        subject="money_signal K[N][R] under STRESSED regime",
        observer_a="TOKEN_HOLDER_DEEP",
        value_a=0.36,   # illustrative; real values come from money_signal
        observer_b="TOKEN_HOLDER_THIN",
        value_b=1.152,
        caveats=(
            "illustrative only; real values come from "
            "money_signal/coupling_observer.py",
            "same regime, different observer position",
        ),
        literature_anchor_key="heterogeneous_agent_macro",
    )
    print("=" * 72)
    print("distributional.signal_asymmetry — observer delta report")
    print("=" * 72)
    print(f"  subject:          {report.subject}")
    print(f"  observers:        {report.observers}")
    print(f"  values:           {report.values}")
    print(f"  delta (B - A):    {report.delta:+.3f}")
    print(f"  asymmetry ratio:  "
          f"{report.asymmetry_ratio:.2f}x" if report.asymmetry_ratio else "undefined")
    print(f"  literature:       {report.literature_anchor_key}")
    print(f"  caveats:")
    for c in report.caveats:
        print(f"    - {c}")
    print()
    print(SISTER_REPO_IMPLEMENTATION_NOTE)


if __name__ == "__main__":
    _demo()
