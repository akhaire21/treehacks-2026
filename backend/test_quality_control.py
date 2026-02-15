"""
Test script for quality control feature (require_close_match).

Demonstrates how the system behaves when require_close_match=True
and no good matches are found after exhausting max_depth.
"""

import json
from config import initialize_services
from orchestrator import MarketplaceOrchestrator


def test_quality_control():
    """Test quality control feature with realistic and unrealistic queries."""

    # Initialize services
    print("="*70)
    print("TESTING QUALITY CONTROL FEATURE")
    print("="*70)
    print("\nInitializing services...")
    initialize_services()

    # Create orchestrator
    orchestrator = MarketplaceOrchestrator()

    # Load workflows
    print("Loading workflows...")
    orchestrator.decomposer.es_service.create_index(delete_existing=False)
    try:
        orchestrator.decomposer.load_and_index_workflows("workflows.json")
    except Exception:
        print("Workflows already indexed")

    print("\n" + "="*70)
    print("TEST 1: Realistic Query (should find matches)")
    print("="*70)

    realistic_query = "I need to file my Ohio 2024 taxes with W2 income"

    # Test WITHOUT quality control
    print("\n[A] Without quality control (require_close_match=False):")
    print(f"Query: {realistic_query}\n")

    response1 = orchestrator.estimate_price_and_search(
        raw_query=realistic_query,
        top_k=3,
        require_close_match=False
    )

    print(f"✓ Number of solutions: {response1['num_solutions']}")
    if response1['num_solutions'] > 0:
        print(f"✓ Best solution cost: {response1['solutions'][0]['pricing']['total_cost_tokens']} tokens")

    # Test WITH quality control
    print("\n[B] With quality control (require_close_match=True):")

    response2 = orchestrator.estimate_price_and_search(
        raw_query=realistic_query,
        top_k=3,
        require_close_match=True
    )

    print(f"✓ Number of solutions: {response2['num_solutions']}")
    if response2['num_solutions'] > 0:
        print(f"✓ Best solution cost: {response2['solutions'][0]['pricing']['total_cost_tokens']} tokens")

    print("\n" + "="*70)
    print("TEST 2: Unrealistic Query (should trigger quality control)")
    print("="*70)

    unrealistic_query = "I need to file taxes for my Mars colony mining operation in 2099"

    # Test WITHOUT quality control
    print("\n[A] Without quality control (require_close_match=False):")
    print(f"Query: {unrealistic_query}\n")

    response3 = orchestrator.estimate_price_and_search(
        raw_query=unrealistic_query,
        top_k=3,
        require_close_match=False
    )

    print(f"✓ Number of solutions: {response3['num_solutions']}")
    if response3['num_solutions'] > 0:
        best_solution = response3['solutions'][0]
        print(f"✓ Best solution cost: {best_solution['pricing']['total_cost_tokens']} tokens")
        print(f"✓ Confidence score: {best_solution['confidence_score']:.3f}")
        print(f"⚠️  Note: Might return poor matches")
    else:
        print("✓ No solutions found")

    # Test WITH quality control
    print("\n[B] With quality control (require_close_match=True):")

    response4 = orchestrator.estimate_price_and_search(
        raw_query=unrealistic_query,
        top_k=3,
        require_close_match=True
    )

    print(f"✓ Number of solutions: {response4['num_solutions']}")

    if 'quality_control' in response4 and response4['quality_control']['triggered']:
        qc = response4['quality_control']
        print(f"\n⚠️  QUALITY CONTROL TRIGGERED:")
        print(f"  Reason: {qc['reason']}")
        print(f"  Max depth reached: {qc['max_depth_reached']}")
        print(f"  Final depth: {qc['final_depth']}")
        print(f"  Best score: {qc['best_score']:.3f}")
        print(f"  Required score: {qc['min_required_score']:.3f}")
        print(f"\n✓ System correctly prevented poor quality matches!")

    print("\n" + "="*70)
    print("TEST 3: Edge Case - Partial Match Query")
    print("="*70)

    partial_query = "File California taxes with crypto gains and rental income from lunar properties"

    print(f"\nQuery: {partial_query}")
    print("\nWith quality control (require_close_match=True):\n")

    response5 = orchestrator.estimate_price_and_search(
        raw_query=partial_query,
        top_k=3,
        require_close_match=True
    )

    print(f"✓ Number of solutions: {response5['num_solutions']}")

    if response5['num_solutions'] > 0:
        print(f"✓ System found partial matches (e.g., CA taxes, crypto, rental)")
        print(f"✓ Best solution cost: {response5['solutions'][0]['pricing']['total_cost_tokens']} tokens")
        print(f"✓ Confidence: {response5['solutions'][0]['confidence_score']:.3f}")
        print(f"✓ Coverage: {response5['solutions'][0]['structure']['coverage']}")
    elif 'quality_control' in response5:
        print(f"⚠️  Quality control triggered - coverage too low")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
The require_close_match parameter provides quality control:

✓ When False (default):
  - Returns best effort results even if matches are weak
  - Useful for exploratory searches
  - Agent can decide whether to use results

✓ When True:
  - Only returns results if confidence is above threshold
  - Prevents charging for poor quality matches
  - Better for production use where quality matters

Configuration:
  - MIN_ACCEPTABLE_SCORE: 0.6 (configurable in .env)
  - MAX_RECURSION_DEPTH: 2 (max search depth)
  - SCORE_THRESHOLD_GOOD: 0.85 (early exit threshold)

Quality control triggers when:
  1. Max recursion depth is reached AND
  2. Best score < MIN_ACCEPTABLE_SCORE
    """)


if __name__ == "__main__":
    test_quality_control()
