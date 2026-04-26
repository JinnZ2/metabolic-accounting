"""
tests/test_counts_consistency.py

Tripwires for scripts/counts_consistency.py (AUDIT_23 Part B).

The counts-consistency table is the defense against silent drift
between STATUS.md / audit-doc claims and codebase reality. If a
declared count diverges from the live count:

  (a) Legitimate change — bump the DECLARED entry in
      scripts/counts_consistency.py AND cite a new AUDIT_XX.md
      that documents why the count changed.
  (b) Silent regression — some code change accidentally bumped a
      count (e.g. removed a historical case, dropped a signal
      score, broke a match). Find and fix it.

Both outcomes require explicit action. The failure mode this
catches is the third: silent drift that nobody notices until
months later when STATUS.md reads like fiction.

Locks in:
  1. All 15 declared counts match the live computation.
  2. No row has drift != 0 (tripwire on silent bumping of one side
     without the other).
  3. Row keys are unique (catches copy-paste errors in DECLARED).
  4. compute_live_counts() returns an int for every declared key
     (catches silent None / KeyError masked by the -1 sentinel).
  5. main() returns 0 at the declared baseline (command-line
     contract).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.counts_consistency import (
    DECLARED, build_rows, compute_live_counts, main, report,
)


def test_1_all_rows_match_declared():
    """LOAD-BEARING: every declared count must match live. This is
    the central invariant of the counts-consistency pattern."""
    print("\n--- TEST 1: all rows match declared baseline ---")
    rows = build_rows()
    drift = [r for r in rows if not r.ok]
    if drift:
        print(report(rows))
        raise AssertionError(
            f"FAIL: {len(drift)} rows drifted from baseline:\n  "
            + "\n  ".join(
                f"{r.key}: declared={r.declared} live={r.live} "
                f"drift={r.drift:+d} anchor={r.anchor}"
                for r in drift
            )
        )
    print(f"  {len(rows)}/{len(rows)} rows match declared baseline")
    print("PASS")


def test_2_no_drift_anywhere():
    """Redundant-seeming with test 1, but stronger failure message
    if someone adds a row without a corresponding live computation
    (yielding drift = live(-1) - declared)."""
    print("\n--- TEST 2: no drift anywhere (live != -1 sentinel) ---")
    rows = build_rows()
    for r in rows:
        assert r.live >= 0, (
            f"FAIL: key {r.key} missing from compute_live_counts "
            f"(live == -1 sentinel)"
        )
        assert r.drift == 0, (
            f"FAIL: {r.key} drift={r.drift:+d} "
            f"(declared={r.declared}, live={r.live})"
        )
    print(f"  no drift, no missing live counts")
    print("PASS")


def test_3_declared_keys_unique():
    """Copy-paste accident guard: if two rows declare the same key,
    the second silently shadows the first. Forcing uniqueness on the
    DECLARED side catches this."""
    print("\n--- TEST 3: declared keys are unique ---")
    keys = [k for (k, _, _, _) in DECLARED]
    seen = set()
    dupes = []
    for k in keys:
        if k in seen:
            dupes.append(k)
        seen.add(k)
    assert not dupes, f"FAIL: duplicate DECLARED keys: {dupes}"
    print(f"  {len(keys)} unique keys")
    print("PASS")


def test_4_live_returns_int_for_each_declared_key():
    """compute_live_counts() must return an int (not None, not a
    string) for every declared key. Masked KeyErrors would show up
    as -1 in build_rows; this catches the other mask: a live key
    returning a non-int value that coerces unexpectedly."""
    print("\n--- TEST 4: live count is int for every declared key ---")
    live = compute_live_counts()
    for (k, _, _, _) in DECLARED:
        assert k in live, f"FAIL: {k} missing from compute_live_counts output"
        v = live[k]
        assert isinstance(v, int), (
            f"FAIL: {k} live value is {type(v).__name__}, expected int"
        )
        assert v >= 0, f"FAIL: {k} live value {v} < 0"
    print(f"  {len(DECLARED)} live values present and int-typed")
    print("PASS")


def test_5_main_returns_zero_at_baseline():
    """Command-line contract: when baseline matches live, `python
    scripts/counts_consistency.py` exits 0. Regression would be
    main() returning non-zero on an all-PASS table."""
    print("\n--- TEST 5: main() returns 0 at declared baseline ---")
    # main() prints to stdout; we just check the exit code.
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main()
    assert rc == 0, f"FAIL: main() returned {rc} at baseline"
    out = buf.getvalue()
    assert "rows match declared baseline" in out, (
        f"FAIL: report body missing expected summary line"
    )
    print(f"  main() exit 0; report summary line present")
    print("PASS")


if __name__ == "__main__":
    test_1_all_rows_match_declared()
    test_2_no_drift_anywhere()
    test_3_declared_keys_unique()
    test_4_live_returns_int_for_each_declared_key()
    test_5_main_returns_zero_at_baseline()
    print("\nall counts_consistency tests passed.")
