"""
tests/test_recovery_pathways.py

Tripwires for term_audit/recovery_pathways.py.

Locks in:
  - dependency graph structure
  - recovery stage sequence
  - collapse depth → recovery time mapping
  - historical case validation
  - preservation strategies for each critical function

Run: python -m tests.test_recovery_pathways
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.civilization_substrate_scaling import (
    ScaleTier, SCALE_ORDER, MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS
)
from term_audit.collapse_propensity import (
    current_civilization_collapse_depth,
    CollapseDepthEstimate,
)
from term_audit.recovery_pathways import (
    FUNCTION_DEPENDENCIES,
    get_dependency_graph,
    get_reverse_dependency_graph,
    FUNCTION_RECOVERY_STAGE,
    RECOVERY_STAGE_ESTIMATES,
    RecoveryStage,
    build_recovery_pathway,
    PRESERVATION_STRATEGIES,
    HISTORICAL_CASES,
    FALSIFIABLE_PREDICTIONS,
)


def test_1_dependency_graph_is_acyclic():
    """The function dependency graph must contain no cycles.
    A cycle would mean two functions each depend on the other,
    which would make recovery sequencing impossible."""
    print("\n--- TEST 1: dependency graph is acyclic ---")
    graph = get_dependency_graph()

    # DFS cycle detection
    visited = set()
    rec_stack = set()

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            assert not has_cycle(node), f"FAIL: cycle detected involving {node}"

    print(f"  {len(graph)} functions, 0 cycles")
    print("PASS")


def test_2_reverse_dependencies_match():
    """The reverse dependency graph should be the exact transpose."""
    print("\n--- TEST 2: reverse dependency graph is transpose ---")
    graph = get_dependency_graph()
    rev_graph = get_reverse_dependency_graph()

    # Check: if A depends on B, then B is in rev_graph with A as dependent
    for func, deps in graph.items():
        for dep in deps:
            assert func in rev_graph.get(dep, set()), \
                f"FAIL: {func} depends on {dep} but {dep} missing {func} in reverse"

    # Check no extra entries
    for dep, dependents in rev_graph.items():
        for func in dependents:
            assert dep in graph.get(func, set()), \
                f"FAIL: {dep} claims {func} dependent but {func} doesn't depend on {dep}"

    print(f"  forward: {sum(len(d) for d in graph.values())} edges")
    print(f"  reverse: {sum(len(d) for d in rev_graph.values())} edges")
    print("PASS")


def test_3_all_functions_have_recovery_stage():
    """Every function in the dependency graph must be assigned a recovery stage."""
    print("\n--- TEST 3: all functions assigned recovery stage ---")
    graph = get_dependency_graph()
    all_funcs = set(graph.keys()) | {
        dep for deps in graph.values() for dep in deps
    }

    missing = []
    for func in all_funcs:
        if func not in FUNCTION_RECOVERY_STAGE:
            missing.append(func)

    assert not missing, f"FAIL: functions missing recovery stage: {missing}"
    print(f"  {len(all_funcs)} functions, all assigned")
    print("PASS")


def test_4_stage_sequence_is_ordered():
    """Recovery stages must be defined in dependency-respecting order."""
    print("\n--- TEST 4: stage sequence respects dependencies ---")
    stage_order = {
        RecoveryStage.IMMEDIATE_SURVIVAL: 0,
        RecoveryStage.SUBSISTENCE_STABILIZATION: 1,
        RecoveryStage.SOCIAL_RECONSTRUCTION: 2,
        RecoveryStage.INFRASTRUCTURE_REBUILDING: 3,
        RecoveryStage.COORDINATION_RESTORATION: 4,
        RecoveryStage.INSTITUTIONAL_MEMORY: 5,
    }

    graph = get_dependency_graph()
    violations = []

    for func, deps in graph.items():
        func_stage = FUNCTION_RECOVERY_STAGE.get(func)
        if func_stage is None:
            continue
        for dep in deps:
            dep_stage = FUNCTION_RECOVERY_STAGE.get(dep)
            if dep_stage is None:
                continue
            if stage_order[func_stage] < stage_order[dep_stage]:
                violations.append(
                    f"{func} (stage {func_stage.value}) depends on "
                    f"{dep} (stage {dep_stage.value})"
                )

    assert not violations, f"FAIL: stage order violations:\n" + "\n".join(violations)
    print(f"  0 stage order violations")
    print("PASS")


def test_5_nation_collapse_pathway_exists():
    """Build recovery pathway from nation-scale collapse under current atrophy."""
    print("\n--- TEST 5: nation collapse pathway builds ---")
    collapse = current_civilization_collapse_depth(ScaleTier.NATION)
    pathway = build_recovery_pathway(collapse)

    assert pathway.starting_scale == collapse.surviving_scale
    assert pathway.target_scale == ScaleTier.NATION
    assert pathway.total_years_min > 0
    assert pathway.total_years_max > pathway.total_years_min
    assert len(pathway.stage_sequence) > 0

    print(f"  start: {pathway.starting_scale.value}")
    print(f"  target: {pathway.target_scale.value}")
    print(f"  years: {pathway.total_years_min:.0f}-{pathway.total_years_max:.0f}")
    print(f"  stages: {len(pathway.stage_sequence)}")
    print("PASS")


def test_6_preservation_strategies_cover_critical_functions():
    """Every minimum viable civilization function should have a preservation strategy."""
    print("\n--- TEST 6: preservation strategies cover critical functions ---")
    covered = {s.function for s in PRESERVATION_STRATEGIES}
    missing = set(MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS) - covered

    assert not missing, f"FAIL: critical functions without preservation strategy: {missing}"
    print(f"  {len(PRESERVATION_STRATEGIES)} strategies, covering {len(covered)} functions")
    print("PASS")


def test_7_historical_cases_have_valid_scales():
    """Historical cases must reference valid ScaleTier values."""
    print("\n--- TEST 7: historical cases have valid scales ---")
    for case in HISTORICAL_CASES:
        assert case.pre_collapse_scale in ScaleTier
        assert case.post_collapse_scale in ScaleTier
        assert case.recovery_scale_achieved in ScaleTier
        # Post-collapse scale should be smaller than pre-collapse
        pre_idx = SCALE_ORDER.index(case.pre_collapse_scale)
        post_idx = SCALE_ORDER.index(case.post_collapse_scale)
        assert post_idx <= pre_idx, \
            f"FAIL: {case.name} post-collapse scale larger than pre-collapse"

    print(f"  {len(HISTORICAL_CASES)} historical cases, all scales valid")
    print("PASS")


def test_8_falsifiable_predictions_registered():
    """Seven falsifiable predictions with correct schema."""
    print("\n--- TEST 8: falsifiable predictions registered ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 7
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    ids = [p["id"] for p in FALSIFIABLE_PREDICTIONS]
    assert ids == list(range(1, 8)), f"FAIL: expected IDs 1-7, got {ids}"
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions")
    print("PASS")


def test_9_recovery_times_scale_with_tiers():
    """Each lost tier should add substantial recovery time."""
    print("\n--- TEST 9: recovery time scales with tiers lost ---")
    scales_to_test = [ScaleTier.NATION, ScaleTier.REGION, ScaleTier.METROPOLIS]

    tier_years = []
    for scale in scales_to_test:
        collapse = current_civilization_collapse_depth(scale)
        pathway = build_recovery_pathway(collapse)
        tier_years.append((collapse.tiers_lost, pathway.total_years_min))

    # More tiers lost should mean more recovery time (monotonic)
    for i in range(len(tier_years) - 1):
        tiers1, years1 = tier_years[i]
        tiers2, years2 = tier_years[i + 1]
        if tiers1 > tiers2:
            assert years1 >= years2, \
                f"FAIL: {tiers1} tiers lost ({years1} years) vs {tiers2} tiers ({years2} years)"

    print(f"  tier-years mapping: {tier_years}")
    print("PASS")


if __name__ == "__main__":
    test_1_dependency_graph_is_acyclic()
    test_2_reverse_dependencies_match()
    test_3_all_functions_have_recovery_stage()
    test_4_stage_sequence_is_ordered()
    test_5_nation_collapse_pathway_exists()
    test_6_preservation_strategies_cover_critical_functions()
    test_7_historical_cases_have_valid_scales()
    test_8_falsifiable_predictions_registered()
    test_9_recovery_times_scale_with_tiers()
    print("\nall recovery_pathways tests passed.")
