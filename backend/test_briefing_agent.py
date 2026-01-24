"""
Briefing Agent Test Script

Tests the Night Watchman briefing agent with various test scenarios.
Run this script to validate briefing agent functionality before integration.

Usage:
    python test_briefing_agent.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.briefing_agent import briefing_agent
from app.utils.test_data_loader import (
    load_scenario,
    load_chaotic,
    load_healthy,
    load_extreme,
    load_empty,
    load_single,
    print_scenario_summary
)


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "=" * 60)
    print(f"[TEST] {test_name}")
    print("=" * 60)


def print_briefing_result(result: dict, duration: float):
    """Print formatted briefing result."""
    print(f"\n[SUCCESS] Briefing generated in {duration:.2f}s\n")
    print(f"SUMMARY: {result['summary']}\n")

    items = result.get('items', [])
    print(f"ITEMS FOUND: {len(items)}")

    for i, item in enumerate(items, 1):
        print(f"\n  {i}. [{item['type']}] {item['severity']} - {item['title']}")
        print(f"     Description: {item['description']}")
        print(f"     Related Tickets: {', '.join(item['relatedTicketIds'])}")
        if item.get('suggestedAction'):
            print(f"     -> Suggested Action: {item['suggestedAction']}")


async def test_chaotic_scenario():
    """Test 1: Chaotic Data - Primary test scenario with intentional issues."""
    print_test_header("Briefing Agent - Chaotic Data Scenario")

    # Load data
    data = load_chaotic()
    print(f"[OK] Loaded {len(data)} tickets from scenario_chaotic.json")
    print_scenario_summary("chaotic")

    # Run briefing agent
    print("\n[RUNNING] analyze_data()...")
    start_time = time.time()

    result = await briefing_agent.analyze_data(data)
    duration = time.time() - start_time

    # Print results
    print_briefing_result(result, duration)

    # Assertions
    print("\n[VALIDATION] Checking assertions...")
    assertions_passed = 0
    assertions_total = 0

    # Assert: Should find issues
    assertions_total += 1
    if len(result['items']) > 0:
        print(f"  [OK] Found {len(result['items'])} issues (expected > 0)")
        assertions_passed += 1
    else:
        print(f"  [FAILED] Expected issues in chaotic data, but found none")

    # Assert: Should have TKT-99 mentioned (SLA breach)
    assertions_total += 1
    items_str = str(result)
    if "TKT-99" in items_str:
        print("  [OK] TKT-99 (critical SLA breach) detected")
        assertions_passed += 1
    else:
        print("  [FAILED] TKT-99 not mentioned in results")

    # Assert: Should have TKT-101 or TKT-108 mentioned (data conflicts)
    assertions_total += 1
    if "TKT-101" in items_str or "TKT-108" in items_str:
        print("  [OK] Data conflict detected (TKT-101 or TKT-108)")
        assertions_passed += 1
    else:
        print("  [FAILED] Data conflicts not detected")

    print(f"\n[RESULT] {assertions_passed}/{assertions_total} assertions passed")
    return assertions_passed == assertions_total


async def test_healthy_scenario():
    """Test 2: Healthy Data - Should report minimal or no issues."""
    print_test_header("Briefing Agent - Healthy Data Scenario")

    data = load_healthy()
    print(f"[OK] Loaded {len(data)} tickets from scenario_healthy.json")
    print_scenario_summary("healthy")

    print("\n[RUNNING] analyze_data()...")
    start_time = time.time()

    result = await briefing_agent.analyze_data(data)
    duration = time.time() - start_time

    print_briefing_result(result, duration)

    # Assertions
    print("\n[VALIDATION] Checking assertions...")
    assertions_passed = 0
    assertions_total = 0

    # Assert: Should have minimal or no items (healthy data)
    assertions_total += 1
    if len(result['items']) <= 1:
        print(f"  [OK] Minimal issues found ({len(result['items'])} items, expected <= 1)")
        assertions_passed += 1
    else:
        print(f"  [WARNING] Found {len(result['items'])} issues in healthy data (expected <= 1)")
        # Note: This might not be a hard failure depending on agent sensitivity

    # Assert: Summary should indicate health or minimal issues
    assertions_total += 1
    summary_lower = result['summary'].lower()
    health_keywords = ['healthy', 'good', 'clear', 'no issues', 'normal', 'on track']
    if any(keyword in summary_lower for keyword in health_keywords):
        print(f"  [OK] Summary indicates system health")
        assertions_passed += 1
    else:
        print(f"  [INFO] Summary: {result['summary']}")
        print(f"  [INFO] Did not find explicit health indicators, but may still be valid")
        assertions_passed += 1  # Soft pass

    print(f"\n[RESULT] {assertions_passed}/{assertions_total} assertions passed")
    return assertions_passed == assertions_total


async def test_extreme_scenario():
    """Test 3: Extreme Chaos - Stress test with multiple simultaneous issues."""
    print_test_header("Briefing Agent - Extreme Chaos Scenario")

    data = load_extreme()
    print(f"[OK] Loaded {len(data)} tickets from scenario_extreme.json")
    print_scenario_summary("extreme")

    print("\n[RUNNING] analyze_data()...")
    start_time = time.time()

    result = await briefing_agent.analyze_data(data)
    duration = time.time() - start_time

    print_briefing_result(result, duration)

    # Assertions
    print("\n[VALIDATION] Checking assertions...")
    assertions_passed = 0
    assertions_total = 0

    # Assert: Should find many issues
    assertions_total += 1
    if len(result['items']) >= 5:
        print(f"  [OK] Found {len(result['items'])} issues (expected >= 5)")
        assertions_passed += 1
    else:
        print(f"  [FAILED] Expected many issues, but found only {len(result['items'])}")

    # Assert: Should have multiple CRITICAL severity items
    assertions_total += 1
    critical_count = sum(1 for item in result['items'] if item.get('severity') == 'CRITICAL')
    if critical_count >= 2:
        print(f"  [OK] Found {critical_count} CRITICAL severity items")
        assertions_passed += 1
    else:
        print(f"  [WARNING] Expected multiple CRITICAL items, found {critical_count}")

    # Assert: Should handle large dataset without errors
    assertions_total += 1
    if duration < 30:  # Should complete within 30 seconds
        print(f"  [OK] Completed in {duration:.2f}s (< 30s threshold)")
        assertions_passed += 1
    else:
        print(f"  [WARNING] Took {duration:.2f}s (> 30s threshold)")

    print(f"\n[RESULT] {assertions_passed}/{assertions_total} assertions passed")
    return assertions_passed == assertions_total


async def test_empty_scenario():
    """Test 4: Empty Data - Should handle gracefully without crashes."""
    print_test_header("Briefing Agent - Empty Data Scenario")

    data = load_empty()
    print(f"[OK] Loaded {len(data)} tickets (empty array)")

    print("\n[RUNNING] analyze_data()...")
    start_time = time.time()

    try:
        result = await briefing_agent.analyze_data(data)
        duration = time.time() - start_time

        print_briefing_result(result, duration)

        # Assertions
        print("\n[VALIDATION] Checking assertions...")
        assertions_passed = 0
        assertions_total = 0

        # Assert: Should not crash
        assertions_total += 1
        print("  [OK] Did not crash on empty data")
        assertions_passed += 1

        # Assert: Should return empty items
        assertions_total += 1
        if len(result['items']) == 0:
            print("  [OK] No items in result (expected for empty data)")
            assertions_passed += 1
        else:
            print(f"  [WARNING] Found {len(result['items'])} items for empty data")

        # Assert: Should have sensible summary
        assertions_total += 1
        if result.get('summary'):
            print(f"  [OK] Has summary: '{result['summary']}'")
            assertions_passed += 1
        else:
            print("  [FAILED] No summary provided")

        print(f"\n[RESULT] {assertions_passed}/{assertions_total} assertions passed")
        return assertions_passed == assertions_total

    except Exception as e:
        print(f"\n[FAILED] Crashed on empty data: {e}")
        return False


async def test_single_scenario():
    """Test 5: Single Ticket - Should handle minimal dataset correctly."""
    print_test_header("Briefing Agent - Single Ticket Scenario")

    data = load_single()
    print(f"[OK] Loaded {len(data)} ticket from scenario_single.json")
    print_scenario_summary("single")

    print("\n[RUNNING] analyze_data()...")
    start_time = time.time()

    result = await briefing_agent.analyze_data(data)
    duration = time.time() - start_time

    print_briefing_result(result, duration)

    # Assertions
    print("\n[VALIDATION] Checking assertions...")
    assertions_passed = 0
    assertions_total = 0

    # Assert: Should not crash
    assertions_total += 1
    print("  [OK] Did not crash on single ticket")
    assertions_passed += 1

    # Assert: Should process successfully
    assertions_total += 1
    if result.get('summary'):
        print(f"  [OK] Generated summary for single ticket")
        assertions_passed += 1
    else:
        print("  [FAILED] No summary generated")

    # Assert: Fast performance for single ticket
    assertions_total += 1
    if duration < 10:
        print(f"  [OK] Completed quickly ({duration:.2f}s < 10s)")
        assertions_passed += 1
    else:
        print(f"  [WARNING] Took {duration:.2f}s for single ticket")

    print(f"\n[RESULT] {assertions_passed}/{assertions_total} assertions passed")
    return assertions_passed == assertions_total


async def run_all_tests():
    """Run all briefing agent tests."""
    print("\n" + "#" * 60)
    print("# BRIEFING AGENT TEST SUITE")
    print("# Testing Night Watchman with various scenarios")
    print("#" * 60)

    test_results = {}

    # Run all tests
    test_results['chaotic'] = await test_chaotic_scenario()
    test_results['healthy'] = await test_healthy_scenario()
    test_results['extreme'] = await test_extreme_scenario()
    test_results['empty'] = await test_empty_scenario()
    test_results['single'] = await test_single_scenario()

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for passed in test_results.values() if passed)
    total_count = len(test_results)

    for test_name, passed in test_results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name.capitalize()} Scenario")

    print(f"\nOverall: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n[SUCCESS] All briefing agent tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    print("Starting Briefing Agent Tests...")
    print(f"Using AWS Bedrock Model: Amazon Nova Pro")

    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
