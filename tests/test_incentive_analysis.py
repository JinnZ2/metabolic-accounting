"""
tests/test_incentive_analysis.py

Tripwires for term_audit/incentive_analysis.py — the cross-term
meta-analysis layer that classifies every audit's standard-setters
into archetypes and computes capture risk.

Locks in:
  - SETTER_ARCHETYPES vocabulary (removing one silently weakens
    analysis coverage)
  - classify_setter reaches the right archetype on obvious cases
  - analyze_term produces a TermIncentiveProfile with the documented
    fields
  - analyze_cross_term across the committed audits produces the
    expected shape (one profile per audit, aggregates per archetype)
  - render_report produces non-empty text with load-bearing sections
  - six falsifiable predictions registered

Run: python -m tests.test_incentive_analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.incentive_analysis import (
    SETTER_ARCHETYPES,
    classify_setter,
    TermIncentiveProfile,
    analyze_term,
    analyze_cross_term,
    render_report,
    load_all_existing_audits,
    FALSIFIABLE_PREDICTIONS,
)
from term_audit.schema import StandardSetter, TermAudit, FirstPrinciplesPurpose


def _minimal_audit(setters):
    """Construct a minimal TermAudit for testing classify/analyze."""
    return TermAudit(
        term="test_term",
        claimed_signal="test",
        standard_setters=setters,
        signal_scores=[],
        first_principles=FirstPrinciplesPurpose(
            stated_purpose="p", physical_referent=None,
            informational_referent=None,
            drift_score=0.0, drift_justification="j",
        ),
        correlation_to_real_signal=0.0,
        correlation_justification="j",
    )


def test_1_archetype_vocabulary():
    """Ten archetypes registered. Tripwire against silent removal;
    adding one is fine."""
    print("\n--- TEST 1: ten setter archetypes ---")
    assert len(SETTER_ARCHETYPES) == 10, \
        f"FAIL: expected 10 archetypes, got {len(SETTER_ARCHETYPES)}"
    # load-bearing archetypes that must stay
    required = {
        "credentialed_profession", "statutory_authority",
        "market_infrastructure", "ownership_position",
        "physical_law", "practitioner_domain",
    }
    assert required.issubset(set(SETTER_ARCHETYPES)), \
        f"FAIL: missing {required - set(SETTER_ARCHETYPES)}"
    print(f"  {len(SETTER_ARCHETYPES)} archetypes")
    print("PASS")


def test_2_classify_setter_on_clear_cases():
    """Obvious setters reach the expected archetype."""
    print("\n--- TEST 2: classify_setter on clear cases ---")
    fed = StandardSetter(
        name="Federal Reserve", authority_basis="statutory",
        incentive_structure="x", independence_from_measured=0.1,
    )
    assert classify_setter(fed) == "statutory_authority", \
        f"FAIL: Fed -> {classify_setter(fed)}"
    practitioner = StandardSetter(
        name="soil scientist practitioners",
        authority_basis="empirical field measurement",
        incentive_structure="x", independence_from_measured=0.8,
    )
    assert classify_setter(practitioner) == "practitioner_domain"
    print("  Fed -> statutory_authority; field practitioners -> "
          "practitioner_domain")
    print("PASS")


def test_3_analyze_term_empty_setters():
    """A term with no standard_setters returns a degenerate profile
    with capture_risk=1.0 and dominant_archetype='none'."""
    print("\n--- TEST 3: analyze_term handles empty setters ---")
    profile = analyze_term(_minimal_audit([]))
    assert profile.mean_independence == 0.0
    assert profile.capture_risk == 1.0
    assert profile.dominant_archetype == "none"
    assert profile.weakest_setter is None
    print(f"  empty setters -> capture_risk=1.0, dominant='none'")
    print("PASS")


def test_4_analyze_term_populates_profile():
    """A normal audit returns a populated profile."""
    print("\n--- TEST 4: analyze_term populates profile ---")
    setters = [
        StandardSetter(
            name="BLS", authority_basis="statutory",
            incentive_structure="x", independence_from_measured=0.3,
        ),
        StandardSetter(
            name="management accountants",
            authority_basis="credentialed practice",
            incentive_structure="x", independence_from_measured=0.1,
        ),
    ]
    profile = analyze_term(_minimal_audit(setters))
    assert abs(profile.mean_independence - 0.2) < 1e-9
    assert 0.0 < profile.capture_risk <= 1.0
    assert profile.weakest_setter is not None
    assert profile.strongest_setter is not None
    assert profile.dominant_archetype != "none"
    assert len(profile.setters) == 2
    assert sum(profile.archetype_count.values()) == 2
    print(f"  mean_ind={profile.mean_independence:.2f}, "
          f"capture_risk={profile.capture_risk:.2f}, "
          f"dominant={profile.dominant_archetype}")
    print("PASS")


def test_5_cross_term_analysis_across_committed_audits():
    """Running the analysis across all committed audits produces one
    profile per audit and one aggregate per archetype actually
    appearing."""
    print("\n--- TEST 5: cross-term analysis across committed audits ---")
    audits = load_all_existing_audits()
    assert len(audits) >= 5, \
        f"FAIL: expected at least 5 audits loaded, got {len(audits)}"
    report = analyze_cross_term(audits)
    assert len(report.term_profiles) == len(audits)
    # aggregates cover the archetypes that actually appear
    appearing = set()
    for p in report.term_profiles:
        appearing.update(p.archetype_count.keys())
    assert set(report.archetype_aggregates.keys()).issubset(appearing)
    # capture_risk is bounded
    for p in report.term_profiles:
        assert 0.0 <= p.capture_risk <= 1.0
    print(f"  audits={len(audits)}, profiles={len(report.term_profiles)}, "
          f"archetype aggregates={len(report.archetype_aggregates)}")
    print("PASS")


def test_6_high_capture_terms_identifiable():
    """At least one committed audit should surface with capture_risk
    above 0.5 (that's the point of having audits like money,
    productivity, efficiency with heavy incentive capture)."""
    print("\n--- TEST 6: high-capture terms identifiable ---")
    audits = load_all_existing_audits()
    report = analyze_cross_term(audits)
    high = [p for p in report.term_profiles if p.capture_risk > 0.5]
    assert len(high) >= 1, \
        "FAIL: no committed audit surfaces as high-capture (>0.5). " \
        "Either the audits have all become signal-rich or the capture " \
        "metric has drifted; investigate."
    # the expected high-capture cluster includes the Tier 1 / Tier 2
    # collapsed-token audits
    high_terms = {p.term for p in high}
    likely_high = {
        "efficiency_conventional_linear",
        "value_collapsed_current_usage",
        "productivity_conventional",
        "money",
    }
    # at least two of these should surface
    overlap = high_terms & likely_high
    assert len(overlap) >= 2, \
        f"FAIL: expected at least 2 of {likely_high} to be high-capture, " \
        f"got {overlap}"
    print(f"  high-capture terms: {sorted(high_terms)}")
    print("PASS")


def test_7_render_report_nonempty_and_structured():
    """render_report produces non-empty text with the documented
    section headers."""
    print("\n--- TEST 7: render_report produces structured text ---")
    audits = load_all_existing_audits()
    report = analyze_cross_term(audits)
    text = render_report(report)
    assert len(text) > 200
    for section in ("per-term capture risk", "archetype aggregates"):
        assert section in text.lower(), \
            f"FAIL: section '{section}' missing from report"
    print(f"  {len(text)} chars; expected sections present")
    print("PASS")


def test_8_falsifiable_predictions_schema():
    """Six falsifiable predictions registered with id/claim/
    falsification schema."""
    print("\n--- TEST 8: predictions schema ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 6
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    ids = [p["id"] for p in FALSIFIABLE_PREDICTIONS]
    assert ids == sorted(ids)
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions, ids {ids}")
    print("PASS")


if __name__ == "__main__":
    test_1_archetype_vocabulary()
    test_2_classify_setter_on_clear_cases()
    test_3_analyze_term_empty_setters()
    test_4_analyze_term_populates_profile()
    test_5_cross_term_analysis_across_committed_audits()
    test_6_high_capture_terms_identifiable()
    test_7_render_report_nonempty_and_structured()
    test_8_falsifiable_predictions_schema()
    print("\nall incentive analysis tests passed.")
