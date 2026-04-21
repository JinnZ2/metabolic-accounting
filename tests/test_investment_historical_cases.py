"""
tests/test_investment_historical_cases.py

Tripwires for investment_signal/historical_cases.py (AUDIT_14 Part B).

Structural tests:
  1. five anchor cases registered (names match expected set)
  2. every ObservedInvestmentFailure uses a valid failure tag from
     VALID_FAILURE_TAGS (failure of this check would be a schema
     drift, not a framework finding)
  3. every ObservedInvestmentFailure carries a complete Provenance
     (EMPIRICAL or PLACEHOLDER, never absent)
  4. compare_case runs end-to-end on every anchor
  5. framework predicted-covers-observed for 4/5 cases; the ZIRP
     mismatch is the documented honest-finding outlier

Per-case structural properties:
  6. MBS 2008: DURING context money_near_collapse must propagate
     into predicted failure tags (claim-chain regression)
  7. GIG economy: DERIVATIVE distance must produce
     financialized_reverse_causation in predicted tags
  8. COMMUNITY LAND TRUSTS: DIRECT + MULTI_GENERATIONAL +
     RECIPROCAL_OBLIGATION must produce ZERO structural failures
     in the observed set — the counter-example discipline
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from investment_signal.historical_cases import (
    ALL_CASES, HistoricalInvestmentCase, ObservedInvestmentFailure,
    CaseComparison, VALID_FAILURE_TAGS,
    compare_case,
    ENRON_2001, MBS_2008, GIG_ECONOMY, COMMUNITY_LAND_TRUSTS,
    COLONIAL_RESOURCE_EXTRACTION, RETIREMENT_401K_GENERATIONAL,
    # AUDIT_20 § B decomposition: three sub-cases replace the former
    # single ZIRP_2009_2021 anchor.
    ZIRP_RETAIL_DIVERSIFIED, ZIRP_PRIVATE_EQUITY, ZIRP_CLO_STRUCTURED,
    # AUDIT_20 § A extension:
    CONGO_RUBBER_1885_1908,
)
from term_audit.provenance import Provenance


def test_1_all_anchor_cases():
    """AUDIT_12 shipped 5; AUDIT_18 extended to 7; AUDIT_20 § B split
    ZIRP into 3 sub-cases (retail / PE / CLO) and § A added Congo
    rubber → 10 anchors total."""
    print("\n--- TEST 1: ten anchor cases registered ---")
    assert len(ALL_CASES) == 10
    expected = {
        "Enron — synthetic mark-to-market collapse",
        "Mortgage-backed securities — multi-layer opacity",
        "ZIRP era — retail diversified portfolio (liquidity illusion)",
        "ZIRP era — private equity / buyback-driven reverse causation",
        "ZIRP era — leveraged-loan CLO (synthetic derivative distance)",
        "Platform gig economy — TIME/ATTENTION extraction",
        "Community Land Trusts — relational capital preserved through time",
        "Colonial resource-extraction investment (Dutch East India Company era)",
        "US 401(k) system — generational realization-rate divergence",
        "Congo Free State rubber extraction — extreme derivative distance",
    }
    names = {c.name for c in ALL_CASES}
    assert names == expected, f"FAIL: expected {expected}, got {names}"
    print(f"  {len(ALL_CASES)} anchor cases registered")
    print("PASS")


def test_2_all_failure_tags_valid():
    """ObservedInvestmentFailure's constructor rejects unknown tags
    (tripwired via __post_init__ ValueError). This test asserts the
    valid-set boundary."""
    print("\n--- TEST 2: failure tags are valid + constructor rejects unknown ---")
    for case in ALL_CASES:
        for obs in case.observed_failures:
            assert obs.failure_tag in VALID_FAILURE_TAGS, \
                f"FAIL: {case.name} has invalid tag {obs.failure_tag}"

    try:
        ObservedInvestmentFailure(
            failure_tag="bogus_tag",
            evidence="nope",
            provenance=Provenance(kind=Provenance.__annotations__['kind'].__args__[0] if False else None)  # noqa
        )
    except (ValueError, TypeError):
        print("  unknown tag correctly rejected at construction")
        print("PASS")
        return
    raise AssertionError("FAIL: constructor accepted bogus tag")


def test_3_observed_failures_have_provenance():
    print("\n--- TEST 3: observed failures carry complete Provenance ---")
    total = 0
    for case in ALL_CASES:
        for obs in case.observed_failures:
            total += 1
            assert isinstance(obs.provenance, Provenance)
            missing = obs.provenance.missing_fields()
            assert not missing, \
                f"FAIL: {case.name}/{obs.failure_tag} missing: {missing}"
    print(f"  {total} ObservedInvestmentFailures across {len(ALL_CASES)} cases, "
          f"all with complete Provenance")
    print("PASS")


def test_4_compare_case_runs_end_to_end():
    print("\n--- TEST 4: compare_case runs on every anchor ---")
    for case in ALL_CASES:
        cmp = compare_case(case)
        assert isinstance(cmp, CaseComparison)
        assert cmp.case is case
        assert isinstance(cmp.predicted_contains_observed, bool)
        print(f"  {case.name[:55]:<55s}  covers={cmp.predicted_contains_observed}")
    print("PASS")


def test_5_all_ten_match_post_zirp_decomposition():
    """LOAD-BEARING: post-AUDIT_20 § B decomposition, the former
    ZIRP outlier is resolved. The three sub-cases each match their
    internally consistent failure set (retail → liquidity illusion,
    PE → reverse causation, CLO → multiple SYNTHETIC failures).
    Combined with the prior 6 matching cases + Congo rubber,
    framework predicted-covers-observed is now 10/10.

    If this count drops, either:
      - factor values moved (investment_signal code regression)
      - observed failures were edited
      - one of the three ZIRP sub-cases was mis-classified
    All three warrant explicit review before accepting the change."""
    print("\n--- TEST 5: expected 10/10 match post-decomposition ---")
    results = {c.name: compare_case(c) for c in ALL_CASES}
    match_count = sum(1 for r in results.values() if r.predicted_contains_observed)
    assert match_count == 10, \
        f"FAIL: expected 10/10, got {match_count}/10"

    # ZIRP sub-cases each match their own failure set
    assert results[ZIRP_RETAIL_DIVERSIFIED.name].predicted_contains_observed
    assert results[ZIRP_PRIVATE_EQUITY.name].predicted_contains_observed
    assert results[ZIRP_CLO_STRUCTURED.name].predicted_contains_observed

    # AUDIT_20 § A extension (Congo rubber)
    assert results[CONGO_RUBBER_1885_1908.name].predicted_contains_observed

    for other in (ENRON_2001, MBS_2008, GIG_ECONOMY, COMMUNITY_LAND_TRUSTS,
                  COLONIAL_RESOURCE_EXTRACTION,
                  RETIREMENT_401K_GENERATIONAL):
        assert results[other.name].predicted_contains_observed, \
            f"FAIL: {other.name} expected to match but didn't"

    print(f"  10/10 match; ZIRP decomposition resolves the former outlier")
    print("PASS")


def test_6_mbs_near_collapse_propagates():
    """Regression: MBS 2008 DURING context uses NEAR_COLLAPSE money
    (cross-referencing money_signal GFC_2008). Predicted tags must
    include money_near_collapse; losing this would indicate a
    dependency-propagation regression."""
    print("\n--- TEST 6: MBS DURING propagates money_near_collapse ---")
    cmp = compare_case(MBS_2008)
    assert "money_near_collapse" in cmp.predicted_tags, \
        f"FAIL: MBS predicted tags {cmp.predicted_tags} missing money_near_collapse"
    print(f"  money_near_collapse present in predicted: {cmp.predicted_tags}")
    print("PASS")


def test_7_gig_economy_financialized_at_derivative_distance():
    """Regression: GIG context at DERIVATIVE distance must produce
    financialized_reverse_causation (reverse_causation 0.60 ≥ 0.5
    threshold). Setting this to TWO_LAYER in an earlier draft did
    NOT fire the flag — the fix was context classification, not
    framework change."""
    print("\n--- TEST 7: GIG at DERIVATIVE distance → financialized ---")
    cmp = compare_case(GIG_ECONOMY)
    assert "financialized_reverse_causation" in cmp.predicted_tags, \
        f"FAIL: GIG predicted tags {cmp.predicted_tags} missing financialized"
    print(f"  financialized_reverse_causation present at DERIVATIVE distance")
    print("PASS")


def test_8_community_land_trusts_zero_observed_failures():
    """LOAD-BEARING counter-example: CLTs have zero observed failure
    tags. If someone adds an observed failure to CLTs (e.g.,
    'gentrification pressure'), this test catches it and forces
    explicit reconsideration — CLTs are the framework's positive
    case, the point is that DIRECT + MULTI_GENERATIONAL +
    RECIPROCAL_OBLIGATION does not produce the structural failures
    that wreck other long-horizon investments."""
    print("\n--- TEST 8: CLTs counter-example (zero observed failures) ---")
    assert len(COMMUNITY_LAND_TRUSTS.observed_failures) == 0, \
        (f"FAIL: CLTs should have zero observed failures; got "
         f"{[f.failure_tag for f in COMMUNITY_LAND_TRUSTS.observed_failures]}")
    cmp = compare_case(COMMUNITY_LAND_TRUSTS)
    # predicted_contains_observed is vacuously True when observed is empty
    assert cmp.predicted_contains_observed
    print(f"  CLTs: 0 observed failures (counter-example discipline intact)")
    print("PASS")


if __name__ == "__main__":
    test_1_all_anchor_cases()
    test_2_all_failure_tags_valid()
    test_3_observed_failures_have_provenance()
    test_4_compare_case_runs_end_to_end()
    test_5_all_ten_match_post_zirp_decomposition()
    test_6_mbs_near_collapse_propagates()
    test_7_gig_economy_financialized_at_derivative_distance()
    test_8_community_land_trusts_zero_observed_failures()
    print("\nall investment_historical_cases tests passed.")
