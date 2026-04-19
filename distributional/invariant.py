"""
distributional/invariant.py

Distributional invariant in THERMODYNAMIC UNITS ONLY.

When a firm imposes thermodynamic distress, the distress lands somewhere.
This module tracks WHERE in capacity-unit terms:

  - firm_internal_absorption    (capacity the firm pulls from its own
                                 operations: reserve drawdown, internal
                                 redundancy loss)
  - worker_absorption           (members of worker cohorts who crossed
                                 their cliff this period — irreplaceable
                                 tacit knowledge / operational capacity)
  - institutional_absorption    (members of institutional cohorts who
                                 crossed their cliff — agency staff
                                 collapse, permit officer burnout,
                                 inspector shortage)
  - community_absorption        (members of community cohorts who
                                 crossed their cliff — public-service
                                 workers, local caregivers, generational
                                 knowledge holders)

NO CURRENCY. NO PRICING. A collapsed member produces zero output. No
wage adjustment brings them back. No credit expansion creates more of
them. This is the unfakeable measurement the framework needs.

Price can move all these numbers on paper; it cannot move the physical
state of a worker whose cognitive buffer has been exceeded.

The invariant closes in CAPACITY UNITS:
  sum(absorbed_capacity_units) <= total_distress_imposed
The residual (distress not yet attributed to any cohort) is the
framework's signal of incompletely-modeled externalization — likely
future cohort collapses or externalization to cohorts not yet
represented in the model.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .access import AccessReport, PopulationCohort


@dataclass
class DistributionalBalance:
    """Where imposed distress lands, in pure capacity units.

    total_distress_imposed: normalized 0.0-1.0, the firm's structural
        load on its environment this period. Derived from tier and
        basin state. Equal to structural_load from the AccessReport.

    The absorption fields are in CAPACITY UNITS (output potential of
    collapsed members, lost this period). No currency translation.
    """
    total_distress_imposed: float

    firm_internal_capacity_lost: float
    worker_capacity_lost: float
    institutional_capacity_lost: float
    community_capacity_lost: float

    worker_cliffs_crossed: int
    institutional_cliffs_crossed: int
    community_cliffs_crossed: int

    # residual: distress imposed but not yet attributed to any cohort.
    # In pure capacity units this is measured as the delta between
    # imposed load and load actually absorbed by visible cohorts.
    # Residual > 0 indicates externalization to cohorts not yet
    # modeled — likely future cliff crossings or unmodeled stakeholders.
    residual_load: float = 0.0

    # externalization ratio: capacity lost OUTSIDE the firm, divided
    # by total capacity lost. Dimensionless.
    externalization_ratio: float = 0.0

    def total_capacity_lost(self) -> float:
        return (self.firm_internal_capacity_lost
                + self.worker_capacity_lost
                + self.institutional_capacity_lost
                + self.community_capacity_lost)

    def total_cliffs_crossed(self) -> int:
        return (self.worker_cliffs_crossed
                + self.institutional_cliffs_crossed
                + self.community_cliffs_crossed)

    def summary_text(self) -> str:
        lines = [
            f"Distributional balance (capacity units, no price):",
            f"  total structural load imposed: {self.total_distress_imposed:.3f}",
            f"  total capacity lost:           {self.total_capacity_lost():.3f}",
            f"    firm internal:               {self.firm_internal_capacity_lost:.3f}",
            f"    worker cohorts:              {self.worker_capacity_lost:.3f}",
            f"    institutional cohorts:       {self.institutional_capacity_lost:.3f}",
            f"    community cohorts:           {self.community_capacity_lost:.3f}",
            "",
            f"  total cliff crossings:         {self.total_cliffs_crossed()}",
            f"    worker:                      {self.worker_cliffs_crossed}",
            f"    institutional:               {self.institutional_cliffs_crossed}",
            f"    community:                   {self.community_cliffs_crossed}",
            "",
            f"  residual load (unaccounted):   {self.residual_load:.3f}",
            f"  externalization ratio:         {self.externalization_ratio:.2%}",
        ]
        return "\n".join(lines)


def compute_distributional_balance(
    access_report: AccessReport,
    firm_internal_capacity_lost: float = 0.0,
    cohort_classification: Optional[Dict[str, str]] = None,
) -> DistributionalBalance:
    """Compute the distributional balance from an access report.

    cohort_classification: cohort_name -> classification in
        {"worker", "institutional", "community"}. If not provided,
        defaults are inferred from cohort name patterns or all
        cohorts are classified as "worker".

    firm_internal_capacity_lost: capacity the firm itself absorbed
        this period — from reserve drawdown, internal redundancy
        loss, or other firm-internal thermodynamic sinks. Expressed
        in the same capacity units as cohort output (can be 0.0 if
        the firm is externalizing everything).
    """
    classification = cohort_classification or {}

    worker_loss = 0.0
    inst_loss = 0.0
    comm_loss = 0.0
    worker_cliffs = 0
    inst_cliffs = 0
    comm_cliffs = 0

    for name, cohort in access_report.cohorts.items():
        cls = classification.get(name, _default_classify(name))
        newly = access_report.newly_collapsed_this_period.get(name, 0)
        # capacity lost this period from new cliff crossings
        capacity_lost = newly * cohort.baseline_output_per_member

        if cls == "institutional":
            inst_loss += capacity_lost
            inst_cliffs += newly
        elif cls == "community":
            comm_loss += capacity_lost
            comm_cliffs += newly
        else:  # default: worker
            worker_loss += capacity_lost
            worker_cliffs += newly

    total_lost = (firm_internal_capacity_lost + worker_loss
                  + inst_loss + comm_loss)

    # residual in load units: the imposed load minus the fraction of
    # load that converted into observed cliff crossings. If imposed
    # load is 0.85 but we saw crossings for only 30% of the at-risk
    # population, residual load reflects stress absorbed into buffers
    # that haven't yet reached cliff — latent distress.
    total_baseline = access_report.total_baseline_capacity()
    if total_baseline > 0:
        observed_collapse_fraction = (
            (worker_loss + inst_loss + comm_loss) / total_baseline
        )
    else:
        observed_collapse_fraction = 0.0

    residual = max(0.0, access_report.structural_load - observed_collapse_fraction)

    externalized = worker_loss + inst_loss + comm_loss
    if total_lost > 0:
        externalization_ratio = externalized / total_lost
    else:
        externalization_ratio = 0.0

    return DistributionalBalance(
        total_distress_imposed=access_report.structural_load,
        firm_internal_capacity_lost=firm_internal_capacity_lost,
        worker_capacity_lost=worker_loss,
        institutional_capacity_lost=inst_loss,
        community_capacity_lost=comm_loss,
        worker_cliffs_crossed=worker_cliffs,
        institutional_cliffs_crossed=inst_cliffs,
        community_cliffs_crossed=comm_cliffs,
        residual_load=residual,
        externalization_ratio=externalization_ratio,
    )


def _default_classify(cohort_name: str) -> str:
    """Infer cohort classification from name patterns."""
    n = cohort_name.lower()
    if any(k in n for k in ("worker", "employee", "staff", "labor",
                             "skilled", "trade", "operator")):
        return "worker"
    if any(k in n for k in ("institution", "agency", "regulator",
                             "permit", "inspector", "government",
                             "municipal")):
        return "institutional"
    if any(k in n for k in ("community", "resident", "local",
                             "public", "caregiver", "elder",
                             "neighborhood")):
        return "community"
    return "worker"
