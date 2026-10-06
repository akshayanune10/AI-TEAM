"""
Tests for Baseline Comparisons and Academic Benchmark Evaluation.
"""

from app.services.simulation_service import SimulationService


def test_benchmark_comparison(sample_students, sample_projects):
    sim = SimulationService()
    results = sim.run_benchmark_comparison(sample_students, sample_projects, target_team_size=4)

    assert len(results) == 3
    method_names = [r["Method"] for r in results]
    assert any("Random" in m for m in method_names)
    assert any("Skill-Only" in m for m in method_names)
    assert any("Proposed" in m for m in method_names)

    rand_res = next(r for r in results if "Random" in r["Method"])
    prop_res = next(r for r in results if "Proposed" in r["Method"])

    # Proposed should outperform random on average quality score
    assert prop_res["Avg Quality Score"] > rand_res["Avg Quality Score"]
