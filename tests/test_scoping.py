"""
tests/test_scoping.py

Locks in the DeclaredScope behavior from term_audit/scoping.py.

Exercises:
  1. An empty declaration is maximally under-scoped
  2. A partial declaration reports exactly the missing dimensions
  3. A complete declaration is adequately scoped
  4. Unknown dimension names are rejected at construction
  5. Whitespace-only declarations do not count as present
  6. scoping_fraction() tracks the declared fraction monotonically
  7. SCOPING_DIMENSIONS covers the fifteen dimensions listed in
     docs/SCOPING_ECONOMIC_TERMS.md

Run:  python -m tests.test_scoping
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.scoping import (
    DeclaredScope, SCOPING_DIMENSIONS, SCOPING_DIMENSION_NAMES,
)


def test_1_empty_declaration_is_under_scoped():
    """An empty DeclaredScope reports every dimension as missing."""
    print("\n--- TEST 1: empty declaration is fully under-scoped ---")
    ds = DeclaredScope(term="money")
    missing = ds.missing_dimensions()
    assert set(missing) == set(SCOPING_DIMENSION_NAMES), \
        f"FAIL: expected all dimensions missing, got {missing}"
    assert not ds.is_adequately_scoped()
    assert ds.scoping_fraction() == 0.0
    print(f"  missing: {len(missing)} / {len(SCOPING_DIMENSION_NAMES)}")
    print(f"  is_adequately_scoped: {ds.is_adequately_scoped()}")
    print("PASS")


def test_2_partial_declaration_reports_missing_precisely():
    """A partial declaration reports exactly the missing dimensions."""
    print("\n--- TEST 2: partial declaration ---")
    ds = DeclaredScope(
        term="money",
        declarations={
            "referent": "medium of exchange",
            "jurisdiction": "US federal",
            "time_horizon": "instantaneous",
        },
    )
    declared = {"referent", "jurisdiction", "time_horizon"}
    expected_missing = set(SCOPING_DIMENSION_NAMES) - declared
    assert set(ds.missing_dimensions()) == expected_missing, \
        f"FAIL: missing mismatch {set(ds.missing_dimensions())} " \
        f"vs {expected_missing}"
    assert not ds.is_adequately_scoped()
    expected_fraction = 3 / len(SCOPING_DIMENSION_NAMES)
    assert abs(ds.scoping_fraction() - expected_fraction) < 1e-9
    print(f"  declared: 3 / {len(SCOPING_DIMENSION_NAMES)}")
    print(f"  scoping_fraction: {ds.scoping_fraction():.3f}")
    print("PASS")


def test_3_complete_declaration_is_adequately_scoped():
    """A declaration covering every dimension is adequately scoped."""
    print("\n--- TEST 3: complete declaration ---")
    decls = {name: f"test declaration for {name}"
             for name in SCOPING_DIMENSION_NAMES}
    ds = DeclaredScope(term="M1_USD_federal", declarations=decls)
    assert ds.is_adequately_scoped()
    assert ds.missing_dimensions() == []
    assert ds.scoping_fraction() == 1.0
    print(f"  is_adequately_scoped: {ds.is_adequately_scoped()}")
    print(f"  scoping_fraction:     {ds.scoping_fraction()}")
    print("PASS")


def test_4_unknown_dimension_names_rejected():
    """Typos in dimension names must raise; silent acceptance would
    weaken the scoping discipline."""
    print("\n--- TEST 4: unknown dimension names rejected ---")
    try:
        DeclaredScope(
            term="capital",
            declarations={
                "referent": "equity capital",
                "jurisdictions": "US",   # typo: should be 'jurisdiction'
            },
        )
    except ValueError as e:
        assert "jurisdictions" in str(e)
        print(f"  raised as expected: {str(e)[:60]}...")
    else:
        assert False, "FAIL: typo should raise ValueError"
    print("PASS")


def test_5_whitespace_declarations_do_not_count():
    """Empty or whitespace-only declarations do not count as declared."""
    print("\n--- TEST 5: whitespace does not count ---")
    ds = DeclaredScope(
        term="money",
        declarations={
            "referent": "",
            "jurisdiction": "   ",
            "time_horizon": "instantaneous",
        },
    )
    missing = set(ds.missing_dimensions())
    assert "referent" in missing, "FAIL: empty string should count as missing"
    assert "jurisdiction" in missing, \
        "FAIL: whitespace-only should count as missing"
    assert "time_horizon" not in missing
    print(f"  'referent' (empty) missing:         "
          f"{'referent' in missing}")
    print(f"  'jurisdiction' (whitespace) missing:"
          f"{'jurisdiction' in missing}")
    print("PASS")


def test_6_scoping_fraction_is_monotone():
    """scoping_fraction() increases monotonically as dimensions are added."""
    print("\n--- TEST 6: scoping_fraction monotone ---")
    decls = {}
    prev = -1.0
    for name in SCOPING_DIMENSION_NAMES:
        decls[name] = f"test value for {name}"
        ds = DeclaredScope(term="money", declarations=dict(decls))
        f = ds.scoping_fraction()
        assert f > prev, f"FAIL: scoping_fraction went {prev} -> {f}"
        prev = f
    assert abs(prev - 1.0) < 1e-9
    print(f"  final fraction: {prev}")
    print("PASS")


def test_7_dimensions_are_fifteen():
    """SCOPING_DIMENSIONS lists the fifteen dimensions documented in
    docs/SCOPING_ECONOMIC_TERMS.md. Removing one silently weakens the
    discipline; this test is the tripwire."""
    print("\n--- TEST 7: fifteen dimensions present ---")
    assert len(SCOPING_DIMENSIONS) == 15, \
        f"FAIL: expected 15 dimensions, got {len(SCOPING_DIMENSIONS)}. " \
        "If you added one, update docs/SCOPING_ECONOMIC_TERMS.md AND " \
        "this test."
    # spot-check that the load-bearing dimensions are named as expected
    required = {
        "referent", "jurisdiction", "time_horizon", "calibration_procedure",
        "standard_setter", "stock_or_flow", "nominal_or_real",
        "accounting_basis",
    }
    assert required.issubset(set(SCOPING_DIMENSION_NAMES)), \
        f"FAIL: missing required dimensions " \
        f"{required - set(SCOPING_DIMENSION_NAMES)}"
    print(f"  {len(SCOPING_DIMENSIONS)} dimensions registered")
    print("PASS")


if __name__ == "__main__":
    test_1_empty_declaration_is_under_scoped()
    test_2_partial_declaration_reports_missing_precisely()
    test_3_complete_declaration_is_adequately_scoped()
    test_4_unknown_dimension_names_rejected()
    test_5_whitespace_declarations_do_not_count()
    test_6_scoping_fraction_is_monotone()
    test_7_dimensions_are_fifteen()
    print("\nall scoping tests passed.")
