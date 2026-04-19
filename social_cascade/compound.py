"""
social_cascade/compound.py

Compound BLACK detection — when both environmental and social substrates
have crossed into irreversibility at the same site.

The structural insight: environmental BLACK and social BLACK are distinct
signals. A firm can be in environmental BLACK (contaminated soil past
cliff, tertiary pool collapsed) without social BLACK (community still
holding together). And a firm can be in social BLACK (community in full
behavioral cascade) without environmental BLACK (ecosystem still intact,
e.g. a deindustrialized town where the factory left but the land is clean).

COMPOUND BLACK is when BOTH are true simultaneously. This is the
signature of a place becoming uninhabitable in the full human sense,
not just the ecological sense. The thermodynamic argument: social
and environmental substrates are coupled, and once both have crossed
cliff, the feedback loops between them lock the site into a state
that no firm-horizon intervention can exit.

Regulatory engagement changes at compound BLACK:
  - In the US, Title VI of the Civil Rights Act of 1964 engages
    alongside CERCLA when the social cascade signatures disproportionately
    affect protected classes (which, per EPA EJScreen data, they do
    ~57% of the time for air pollution and similar for Superfund
    proximity)
  - In the EU, ELD engagement may be joined by the Social Climate
    Fund (Regulation 2023/955) and Just Transition provisions
  - At the site level, this is the signal that the firm is no longer
    a going concern in any meaningful sense — it has destroyed both
    the ecological and social substrates it depended on
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .signatures import CommunitySignatures, is_social_black


@dataclass
class CompoundBlackReport:
    """Report on combined environmental + social BLACK status."""
    environmental_black: bool = False
    social_black: bool = False
    compound_black: bool = False

    # contributing factors
    env_irreversible_metrics: List[str] = field(default_factory=list)
    env_tertiary_past_cliff: List[str] = field(default_factory=list)
    social_signatures: Optional[CommunitySignatures] = None

    # aggregated severity
    aggregate_externalized_load: float = 0.0
    notes: str = ""

    def summary_text(self) -> str:
        lines = []
        if self.compound_black:
            lines.append("COMPOUND BLACK: environmental AND social substrate "
                         "both in irreversibility.")
        elif self.environmental_black:
            lines.append("ENVIRONMENTAL BLACK: ecological substrate in "
                         "irreversibility.")
            if self.social_signatures and self.social_signatures.any_elevated():
                lines.append("  Social signatures elevated but below BLACK threshold.")
        elif self.social_black:
            lines.append("SOCIAL BLACK: community substrate in behavioral "
                         "cascade; environmental substrate still intact.")
        else:
            lines.append("No BLACK signal detected.")

        if self.env_irreversible_metrics:
            lines.append(
                f"  Environmental irreversible metrics: "
                f"{', '.join(self.env_irreversible_metrics)}"
            )
        if self.env_tertiary_past_cliff:
            lines.append(
                f"  Environmental tertiary pools past cliff: "
                f"{', '.join(self.env_tertiary_past_cliff)}"
            )
        if self.social_signatures:
            s = self.social_signatures
            if s.deaths_of_despair_rate > 0:
                lines.append(
                    f"  Deaths of despair: "
                    f"{s.deaths_of_despair_rate:.1f}/100k "
                    f"(baseline 48; delta {s.despair_delta:+.1f})"
                )
            if s.aggregate_externalized_load > 0.1:
                lines.append(
                    f"  Aggregate externalized load: "
                    f"{s.aggregate_externalized_load:.2f} "
                    f"(>= 3.0 is BLACK threshold)"
                )

        return "\n".join(lines)


def build_compound_report(
    environmental_irreversible_metrics: List[str],
    environmental_tertiary_past_cliff: List[str],
    social_signatures: Optional[CommunitySignatures],
) -> CompoundBlackReport:
    """Build a compound BLACK report combining environmental and
    social substrate signals."""
    report = CompoundBlackReport(
        env_irreversible_metrics=list(environmental_irreversible_metrics),
        env_tertiary_past_cliff=list(environmental_tertiary_past_cliff),
        social_signatures=social_signatures,
    )

    # environmental BLACK: any primary irreversibility or any
    # tertiary pool past cliff (the existing framework definition)
    env_black = (
        bool(environmental_irreversible_metrics)
        or bool(environmental_tertiary_past_cliff)
    )
    report.environmental_black = env_black

    # social BLACK: per is_social_black
    if social_signatures is not None:
        report.social_black = is_social_black(social_signatures)
        report.aggregate_externalized_load = (
            social_signatures.aggregate_externalized_load
        )

    # compound BLACK
    report.compound_black = env_black and report.social_black

    # notes
    if report.compound_black:
        report.notes = (
            "Site has crossed into compound irreversibility. Both "
            "ecological and social substrates are past their respective "
            "cliffs. Firm-horizon remediation is insufficient; regulatory "
            "engagement expands to civil rights and just-transition "
            "frameworks in jurisdictions that have them."
        )
    elif env_black and social_signatures and social_signatures.any_elevated():
        report.notes = (
            "Environmental BLACK with elevated social signatures. Social "
            "cascade is underway but has not yet crossed BLACK threshold. "
            "Window remains for preventive community investment."
        )
    elif report.social_black:
        report.notes = (
            "Social BLACK without environmental BLACK. Community substrate "
            "has collapsed despite intact ecology — the deindustrialization "
            "signature. Firm operations have externalized cost to the "
            "social substrate without necessarily damaging the ecological one."
        )

    return report
