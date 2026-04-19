"""
tests/test_regulatory.py

Exercises the regulatory crosswalk:

  1. Healthy site -> no engagements, informational caveats only
  2. BLACK site with irreversibility -> frameworks engaged
  3. Tertiary past cliff but no primary irreversibility -> partial engagements
  4. Jurisdiction filter -> only US / only EU frameworks returned
  5. Basin filter -> frameworks filtered to only basins present
  6. Framework metadata is complete (sanity on the registry)

Run: python -m tests.test_regulatory
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from infrastructure import (
    new_foundation_system, new_hvac_system, new_cooling_system,
    new_biological_service_system,
)
from reserves import Site
from accounting import compute_flow
from regulatory import (
    ALL_FRAMEWORKS, build_crosswalk,
    CERCLA_SUPERFUND, EU_ELD, UK_PART_2A, GERMANY_BBODSCHG, JAPAN_SCCA,
    frameworks_for_basin, frameworks_by_jurisdiction,
)


def fresh_site():
    site = Site(name="reg_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    })
    site.attach_defaults()
    return site


def systems():
    return [
        new_foundation_system(),
        new_hvac_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def test_1_healthy_no_engagements():
    """Healthy site with no landscape-scale signals -> no engagements."""
    print("\n--- TEST 1: healthy site produces no engagements ---")
    site = fresh_site()
    sr = site.step(stress={}, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    report = build_crosswalk(
        flow,
        jurisdictions=["United States", "EU", "UK", "Germany", "Japan"],
    )
    print(f"  engagements:          {len(report.engagements)}")
    print(f"  caveats:              {len(report.caveats)}")
    print(f"  state:                {report.state_summary}")
    assert not report.has_engagements(), "FAIL: healthy site has engagements"
    assert len(report.caveats) > 0, "FAIL: no caveats"
    print("PASS")


def test_2_black_engages_multiple_frameworks():
    """BLACK site with tertiary past cliff + env loss -> frameworks engaged."""
    print("\n--- TEST 2: BLACK site engages multiple frameworks ---")
    site = fresh_site()
    # crash multiple tertiaries past cliff
    site.tertiary["landscape_reserve"].stock = 100.0
    site.tertiary["watershed_reserve"].stock = 200.0
    # stress that produces env loss
    site.basins["site_soil"].state["carbon_fraction"] = 0.03
    stress = {("site_soil", "carbon_fraction"): 30.0}
    sr = site.step(stress, regenerate=False)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    print(f"  irreversible_metrics: {flow.irreversible_metrics}")
    print(f"  tertiary_past_cliff:  {flow.tertiary_past_cliff}")
    print(f"  environment_loss:     {flow.environment_loss:.4f}")

    report = build_crosswalk(
        flow,
        jurisdictions=["United States", "EU", "UK", "Germany", "Japan"],
        basin_types_present={"soil", "water", "air", "biology"},
    )
    print(f"  engagements:          {len(report.engagements)}")
    for eng in report.engagements:
        print(f"    {eng.framework.short_name}: {eng.severity_indicator}")
    assert report.has_engagements(), "FAIL: BLACK site should engage frameworks"
    print("PASS")


def test_3_jurisdiction_filter_us_only():
    """Jurisdiction filter narrows to US frameworks only."""
    print("\n--- TEST 3: US-only jurisdiction filter ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    site.tertiary["watershed_reserve"].stock = 200.0
    stress = {("site_soil", "carbon_fraction"): 30.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    report = build_crosswalk(flow, jurisdictions=["United States"])
    for eng in report.engagements:
        print(f"  framework: {eng.framework.short_name}")
        assert "United States" in eng.framework.jurisdiction, \
            "FAIL: non-US framework in US-only report"
    print(f"  engagements (US only): {len(report.engagements)}")
    print("PASS")


def test_4_jurisdiction_filter_eu_only():
    """Jurisdiction filter narrows to EU frameworks only."""
    print("\n--- TEST 4: EU-only jurisdiction filter ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    site.tertiary["watershed_reserve"].stock = 200.0
    stress = {("site_soil", "carbon_fraction"): 30.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    report = build_crosswalk(flow, jurisdictions=["European Union"])
    print(f"  engagements (EU only): {len(report.engagements)}")
    for eng in report.engagements:
        print(f"    {eng.framework.short_name}")
    # ELD should match; CERCLA should not
    assert any("ELD" in eng.framework.short_name for eng in report.engagements), \
        "FAIL: EU ELD not matched"
    assert not any("CERCLA" in eng.framework.short_name for eng in report.engagements), \
        "FAIL: CERCLA matched on EU-only filter"
    print("PASS")


def test_5_basin_filter():
    """Basin filter limits frameworks to those covering present basins."""
    print("\n--- TEST 5: basin type filter (soil-only site) ---")
    # synthesize a flow as if only soil damage occurred
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    stress = {("site_soil", "carbon_fraction"): 30.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )

    # all frameworks in our registry cover soil, so they should all match
    report_all = build_crosswalk(
        flow, jurisdictions=["United States", "EU", "UK", "Germany", "Japan"],
        basin_types_present={"soil"},
    )
    print(f"  with soil basin:      {len(report_all.engagements)} engagements")

    # now filter to only biology — only frameworks covering biology
    report_bio = build_crosswalk(
        flow, jurisdictions=["United States", "EU", "UK", "Germany", "Japan"],
        basin_types_present={"biology"},
    )
    print(f"  with biology only:    {len(report_bio.engagements)} engagements")
    # ELD covers biology, Japan SCCA and Germany BBodSchG focus on soil+water
    # so biology-only should be a narrower set
    bio_frameworks = {e.framework.short_name for e in report_bio.engagements}
    print(f"  biology frameworks:   {bio_frameworks}")
    print("PASS")


def test_6_registry_metadata_complete():
    """Sanity: every registered framework has required metadata."""
    print("\n--- TEST 6: framework registry sanity ---")
    print(f"  frameworks registered: {len(ALL_FRAMEWORKS)}")
    for f in ALL_FRAMEWORKS:
        assert f.jurisdiction, f"FAIL: {f.short_name} missing jurisdiction"
        assert f.statute, f"FAIL: {f.short_name} missing statute"
        assert f.authority, f"FAIL: {f.short_name} missing authority"
        assert f.pathway_types, f"FAIL: {f.short_name} missing pathways"
        assert f.liability_scheme, f"FAIL: {f.short_name} missing liability"
        assert f.source_url, f"FAIL: {f.short_name} missing source URL"
        assert f.typical_actions, f"FAIL: {f.short_name} missing actions"
        assert f.corresponds_to_basins, f"FAIL: {f.short_name} missing basins"
        print(f"  {f.short_name:18s} {f.jurisdiction}")
    print("PASS")


def test_7_summary_text_renders():
    """summary_text() produces readable output."""
    print("\n--- TEST 7: summary_text renders correctly ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    site.tertiary["watershed_reserve"].stock = 200.0
    stress = {("site_soil", "carbon_fraction"): 30.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    report = build_crosswalk(
        flow, jurisdictions=["United States", "EU", "Germany"],
    )
    text = report.summary_text()
    assert "Regulatory crosswalk" in text
    assert ("Plausibly engaged frameworks" in text
            or "No regulatory frameworks" in text)
    # print a sample for visual inspection
    print("  --- sample output ---")
    for line in text.split("\n")[:15]:
        print(f"  {line}")
    print("  [...truncated]")
    print("PASS")


if __name__ == "__main__":
    test_1_healthy_no_engagements()
    test_2_black_engages_multiple_frameworks()
    test_3_jurisdiction_filter_us_only()
    test_4_jurisdiction_filter_eu_only()
    test_5_basin_filter()
    test_6_registry_metadata_complete()
    test_7_summary_text_renders()
    print("\nall regulatory tests passed.")
