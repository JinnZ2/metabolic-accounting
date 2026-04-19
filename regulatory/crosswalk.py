"""
regulatory/crosswalk.py

Crosswalk from metabolic-accounting verdict state to regulatory frameworks.

Given a GlucoseFlow and the set of jurisdictions a firm operates in,
identify which regulatory frameworks are plausibly engaged by the
current state. Returns informational references, NOT legal determinations.

This is the "toe-in" layer. A firm seeing BLACK in metabolic-accounting
now sees a map to the regulatory frameworks their condition corresponds
to in each jurisdiction they operate in. Across jurisdictions, this
creates comparability: a German BLACK firm and a US BLACK firm can now
be discussed in equivalent measurement terms plus their respective
regulatory coordinates.
"""

from dataclasses import dataclass, field
from typing import List, Set

from accounting.glucose import GlucoseFlow
from .frameworks import (
    RegulatoryFramework, ALL_FRAMEWORKS,
    frameworks_for_basin, frameworks_for_tertiary,
    frameworks_by_jurisdiction,
)


@dataclass
class RegulatoryEngagement:
    """One framework plausibly engaged by current state.

    Engagement is INFORMATIONAL — it says 'a firm in this thermodynamic
    condition would plausibly engage this framework,' not 'this framework
    applies.' Actual applicability requires legal analysis specific to
    the site, activity, and jurisdiction.
    """
    framework: RegulatoryFramework
    engagement_reasons: List[str]          # why this framework is engaged
    severity_indicator: str                 # "notification" / "remediation" /
                                             # "liability" / "designation"
    corresponding_basins: List[str]         # our basin types that match
    corresponding_tertiary: List[str]       # our tertiary pools that match
    our_signals: List[str]                  # signals from GlucoseFlow
                                             # that triggered this


@dataclass
class CrosswalkReport:
    """Report showing all regulatory engagements for current state."""
    jurisdictions_checked: List[str]
    state_summary: str
    engagements: List[RegulatoryEngagement] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)

    def has_engagements(self) -> bool:
        return len(self.engagements) > 0

    def summary_text(self) -> str:
        """Human-readable summary for dashboards and reports."""
        lines = [
            f"Regulatory crosswalk: {self.state_summary}",
            f"Jurisdictions checked: {', '.join(self.jurisdictions_checked)}",
            "",
        ]
        if not self.engagements:
            lines.append("No regulatory frameworks plausibly engaged "
                         "at current state.")
            return "\n".join(lines)

        lines.append(f"Plausibly engaged frameworks: {len(self.engagements)}")
        lines.append("")
        for eng in self.engagements:
            lines.append(f"  {eng.framework.short_name} "
                         f"({eng.framework.jurisdiction})")
            lines.append(f"    severity:  {eng.severity_indicator}")
            lines.append(f"    reasons:")
            for r in eng.engagement_reasons:
                lines.append(f"      - {r}")
            lines.append(f"    threshold: {eng.framework.quantitative_threshold}")
            lines.append(f"    see: {eng.framework.source_url}")
            lines.append("")

        if self.caveats:
            lines.append("Caveats:")
            for c in self.caveats:
                lines.append(f"  - {c}")
        return "\n".join(lines)


def _severity_from_state(flow: GlucoseFlow, framework: RegulatoryFramework) -> str:
    """Map flow state to a severity descriptor for this framework."""
    has_irr = bool(flow.irreversible_metrics)
    has_tertiary_cliff = bool(flow.tertiary_past_cliff)
    has_env_loss = flow.environment_loss > 0

    # primary irreversibility -> most severe regulatory engagement
    if has_irr:
        if framework.triggers_on_primary_irreversibility:
            return "liability"

    # tertiary cliff -> designation / remediation depending on framework
    if has_tertiary_cliff:
        if framework.triggers_on_tertiary_cliff:
            return "remediation"
        return "notification"

    # env loss but no irreversibility yet -> notification-tier
    if has_env_loss:
        return "notification"

    return "monitoring"


def _reasons_from_state(
    flow: GlucoseFlow,
    framework: RegulatoryFramework,
) -> List[str]:
    """Build the human-readable list of reasons this framework is engaged."""
    reasons = []
    # primary irreversibility matching framework's basin coverage
    for metric_id in flow.irreversible_metrics:
        # metric_id format: "basin_name.metric_key"
        if "." in metric_id:
            # detect basin type from metric: we don't have basin_type
            # here, but irreversibility in any basin this framework
            # addresses is sufficient
            reasons.append(
                f"primary irreversibility: {metric_id} "
                "(no amount of firm spend restores this)"
            )
    # tertiary past cliff matching framework's reserve coverage
    for pool in flow.tertiary_past_cliff:
        if pool in framework.corresponds_to_reserves:
            reasons.append(
                f"tertiary pool past cliff: {pool} "
                "(landscape-scale damage signature)"
            )
    # environment loss
    if flow.environment_loss > 0:
        reasons.append(
            f"environment loss this period: {flow.environment_loss:.4g} xdu "
            "(irreversible, second-law signature)"
        )
    return reasons


def _our_signals(flow: GlucoseFlow) -> List[str]:
    signals = []
    if flow.irreversible_metrics:
        signals.append(f"irreversible_metrics ({len(flow.irreversible_metrics)})")
    if flow.tertiary_past_cliff:
        signals.append(f"tertiary_past_cliff ({len(flow.tertiary_past_cliff)})")
    if flow.environment_loss > 0:
        signals.append(f"environment_loss={flow.environment_loss:.4g}")
    if flow.cumulative_environment_loss > 0:
        signals.append(
            f"cumulative_environment_loss={flow.cumulative_environment_loss:.4g}"
        )
    return signals


def build_crosswalk(
    flow: GlucoseFlow,
    jurisdictions: List[str],
    basin_types_present: Set[str] = None,
) -> CrosswalkReport:
    """Build a regulatory crosswalk report.

    flow: the GlucoseFlow for the current period
    jurisdictions: list of jurisdictions to check, e.g.
                   ['United States', 'Germany'] or ['EU'].
                   Also accepts short names: 'CERCLA', 'ELD', etc.
    basin_types_present: optional set of basin types the site has.
                         If provided, only frameworks that cover at
                         least one present basin are included.
                         If None, all frameworks for the specified
                         jurisdictions are checked.
    """
    jurisdictions_normalized = list(jurisdictions)

    # gather candidate frameworks
    candidates: List[RegulatoryFramework] = []
    seen_ids = set()
    for j in jurisdictions:
        for f in frameworks_by_jurisdiction(j):
            fid = f.short_name
            if fid in seen_ids:
                continue
            seen_ids.add(fid)
            candidates.append(f)

    # filter by present basins if specified
    if basin_types_present is not None:
        candidates = [
            f for f in candidates
            if f.corresponds_to_basins & basin_types_present
        ]

    # determine state summary
    state_parts = []
    if flow.irreversible_metrics:
        state_parts.append(
            f"{len(flow.irreversible_metrics)} primary irreversibilities"
        )
    if flow.tertiary_past_cliff:
        state_parts.append(
            f"{len(flow.tertiary_past_cliff)} tertiary pools past cliff"
        )
    if flow.environment_loss > 0:
        state_parts.append(
            f"{flow.environment_loss:.4g} xdu env loss this period"
        )
    if flow.cumulative_environment_loss > 0:
        state_parts.append(
            f"{flow.cumulative_environment_loss:.4g} xdu cumulative env loss"
        )
    state_summary = ("; ".join(state_parts)
                     if state_parts else "no landscape-scale signals")

    report = CrosswalkReport(
        jurisdictions_checked=jurisdictions_normalized,
        state_summary=state_summary,
    )

    # only build engagements if the state has any landscape-scale signal
    has_landscape_signal = (
        bool(flow.irreversible_metrics)
        or bool(flow.tertiary_past_cliff)
        or flow.environment_loss > 0
    )
    if not has_landscape_signal:
        report.caveats.append(
            "Current state does not show landscape-scale signals "
            "(no primary irreversibility, no tertiary cliff, no environment "
            "loss this period). Regulatory frameworks listed below are "
            "informational only; they are not triggered at current state."
        )
        return report

    # build an engagement per candidate framework
    for framework in candidates:
        reasons = _reasons_from_state(flow, framework)
        if not reasons:
            continue
        severity = _severity_from_state(flow, framework)
        matching_basins = list(framework.corresponds_to_basins
                               & (basin_types_present or
                                  framework.corresponds_to_basins))
        matching_tertiary = [
            p for p in flow.tertiary_past_cliff
            if p in framework.corresponds_to_reserves
        ]
        report.engagements.append(RegulatoryEngagement(
            framework=framework,
            engagement_reasons=reasons,
            severity_indicator=severity,
            corresponding_basins=matching_basins,
            corresponding_tertiary=matching_tertiary,
            our_signals=_our_signals(flow),
        ))

    # global caveats
    report.caveats.append(
        "INFORMATIONAL ONLY. This crosswalk does not determine legal "
        "liability or regulatory applicability. Consult counsel for "
        "jurisdiction-specific legal analysis."
    )
    report.caveats.append(
        "Regulatory thresholds vary by substance, pathway, site use, "
        "and ecological context. Our basin-level BLACK signal is a "
        "thermodynamic indicator, not a regulatory determination."
    )

    return report
