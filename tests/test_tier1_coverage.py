"""
tests/test_tier1_coverage.py

Tripwires for the Tier 1 audits (money / value / capital) post-AUDIT_07:

  1. every SignalScore carries a complete Provenance
  2. every linkage (VALUE_LINKAGES / CAPITAL_LINKAGES) carries a
     complete Provenance
  3. the load-bearing negative linkages still have negative sign —
     changing any of these to positive would break the Tier-1-
     inheritance argument (AUDIT_05 § "linkage analysis" named these
     as load-bearing; this test finally tripwires the sign)

AUDIT_07 background: the framework's own discipline ("every numeric
claim needs a source") was not enforced at the call sites. This test
asserts the Tier 1 surface is now fully provenanced.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.money import MONEY_AUDIT
from term_audit.audits.value import ALL_VALUE_AUDITS, VALUE_LINKAGES
from term_audit.audits.capital import ALL_CAPITAL_AUDITS, CAPITAL_LINKAGES
from term_audit.provenance import coverage_report


def _assert_full_coverage(audit, label):
    cov = audit.provenance_coverage()
    assert cov["none"] == 0, \
        f"FAIL: {label} has {cov['none']} signal_scores without provenance"
    assert cov["incomplete"] == 0, \
        (f"FAIL: {label} has {cov['incomplete']} incomplete provenance; "
         f"details: {cov['incomplete_details']}")
    assert cov["complete"] == cov["total"], \
        f"FAIL: {label} coverage mismatch: {cov}"


def test_1_money_audit_fully_provenanced():
    print("\n--- TEST 1: money audit fully provenanced ---")
    _assert_full_coverage(MONEY_AUDIT, "money")
    cov = MONEY_AUDIT.provenance_coverage()
    print(f"  money: {cov['total']}/{cov['total']} scores, "
          f"kinds={cov['by_kind']}")
    print("PASS")


def test_2_value_audits_fully_provenanced():
    print("\n--- TEST 2: value audits fully provenanced ---")
    for key, audit in ALL_VALUE_AUDITS.items():
        _assert_full_coverage(audit, f"value::{key}")
        cov = audit.provenance_coverage()
        print(f"  value::{key}: {cov['complete']}/{cov['total']} "
              f"kinds={cov['by_kind']}")
    print("PASS")


def test_3_capital_audits_fully_provenanced():
    print("\n--- TEST 3: capital audits fully provenanced ---")
    for key, audit in ALL_CAPITAL_AUDITS.items():
        _assert_full_coverage(audit, f"capital::{key}")
        cov = audit.provenance_coverage()
        print(f"  capital::{key}: {cov['complete']}/{cov['total']} "
              f"kinds={cov['by_kind']}")
    print("PASS")


def test_4_value_linkages_fully_provenanced():
    print("\n--- TEST 4: value linkages fully provenanced ---")
    cov = coverage_report([l.provenance for l in VALUE_LINKAGES])
    assert cov["none"] == 0, \
        f"FAIL: {cov['none']} linkages have no provenance"
    assert cov["incomplete"] == 0, \
        f"FAIL: {cov['incomplete']} linkages incomplete: {cov['incomplete_details']}"
    print(f"  {cov['complete']}/{cov['total']} complete, kinds={cov['by_kind']}")
    print("PASS")


def test_5_capital_linkages_fully_provenanced():
    print("\n--- TEST 5: capital linkages fully provenanced ---")
    cov = coverage_report([l.provenance for l in CAPITAL_LINKAGES])
    assert cov["none"] == 0
    assert cov["incomplete"] == 0, \
        f"FAIL: {cov['incomplete_details']}"
    print(f"  {cov['complete']}/{cov['total']} complete, kinds={cov['by_kind']}")
    print("PASS")


def test_6_load_bearing_negative_linkages_stay_negative():
    """The Tier-1-inheritance argument depends on these sign assertions.

    If any of these flips from negative to positive, the 'exchange-value
    substitutes for substrate-value' and 'financial-capital growth is
    substrate extraction' arguments collapse. This test is the tripwire
    AUDIT_05 named but did not encode; AUDIT_07 encodes it.
    """
    print("\n--- TEST 6: load-bearing negative linkages stay negative ---")

    load_bearing = [
        ("V_B", "V_C", VALUE_LINKAGES,
         "exchange-value growth draws down substrate-value"),
        ("K_B", "K_A", CAPITAL_LINKAGES,
         "financial-capital growth draws down productive-capital"),
        ("K_B", "K_C", CAPITAL_LINKAGES,
         "financialization crowds out institutional-capital"),
    ]

    for src, tgt, registry, label in load_bearing:
        matches = [l for l in registry if l.source == src and l.target == tgt]
        assert len(matches) == 1, \
            f"FAIL: expected exactly one {src}->{tgt} linkage, got {len(matches)}"
        link = matches[0]
        assert link.relation == "negative", \
            (f"FAIL: {src}->{tgt} relation is '{link.relation}', must be "
             f"'negative' (load-bearing: {label})")
        assert link.strength_estimate < 0, \
            (f"FAIL: {src}->{tgt} strength_estimate is "
             f"{link.strength_estimate}, must be < 0 (load-bearing: {label})")
        print(f"  {src}->{tgt}  relation={link.relation:9s} "
              f"strength={link.strength_estimate:+.2f}  [{label}]")
    print("PASS")


def test_7_pass_count_vector_is_informative():
    """The bool is_signal() loses information; vector aggregates preserve it.

    The collapsed-vs-decomposed argument's punchline is the gap between
    collapsed (0 passes) and the clean substrate terms (~6-7 passes). A
    bool cannot express this. Assert the scalar aggregates exist and
    differentiate the two regimes.
    """
    print("\n--- TEST 7: vector aggregates differentiate collapsed vs clean ---")
    collapsed_money = MONEY_AUDIT
    collapsed_value = ALL_VALUE_AUDITS["collapsed"]
    substrate_value = ALL_VALUE_AUDITS["V_C_substrate_value"]
    productive_capital = ALL_CAPITAL_AUDITS["K_A_productive"]

    # Collapsed terms: pass_count should be 0 (at 0.7 threshold).
    assert collapsed_money.pass_count() == 0, \
        f"FAIL: money pass_count = {collapsed_money.pass_count()}, want 0"
    assert collapsed_value.pass_count() == 0, \
        f"FAIL: collapsed value pass_count = {collapsed_value.pass_count()}"

    # Clean terms: pass_count >= 5 (the is_signal threshold).
    assert substrate_value.pass_count() >= 5, \
        f"FAIL: V_C pass_count = {substrate_value.pass_count()}, want >= 5"
    assert productive_capital.pass_count() >= 5, \
        f"FAIL: K_A pass_count = {productive_capital.pass_count()}, want >= 5"

    print(f"  money collapsed: pass={collapsed_money.pass_count()} "
          f"mean={collapsed_money.mean_score():.3f} "
          f"min={collapsed_money.min_score():.2f}")
    print(f"  V_C substrate:   pass={substrate_value.pass_count()} "
          f"mean={substrate_value.mean_score():.3f} "
          f"min={substrate_value.min_score():.2f}")
    print(f"  K_A productive:  pass={productive_capital.pass_count()} "
          f"mean={productive_capital.mean_score():.3f} "
          f"min={productive_capital.min_score():.2f}")
    print("PASS")


if __name__ == "__main__":
    test_1_money_audit_fully_provenanced()
    test_2_value_audits_fully_provenanced()
    test_3_capital_audits_fully_provenanced()
    test_4_value_linkages_fully_provenanced()
    test_5_capital_linkages_fully_provenanced()
    test_6_load_bearing_negative_linkages_stay_negative()
    test_7_pass_count_vector_is_informative()
    print("\nall Tier-1 coverage tests passed.")
