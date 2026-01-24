"""
Test Data Loader Utility

Provides functions to load test scenario data for Phase 2 testing.

IMPORTANT: This module is for testing only and will be deprecated
when real data connectors are implemented in Phase 3+.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Get test data directory path
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"


def load_scenario(scenario_name: str) -> List[Dict]:
    """
    Load test scenario data by name.

    Args:
        scenario_name: Name of the scenario (e.g., "chaotic", "healthy", "extreme")

    Returns:
        List of ticket dictionaries

    Raises:
        FileNotFoundError: If scenario file doesn't exist
        json.JSONDecodeError: If JSON is malformed

    Example:
        >>> chaotic_data = load_scenario("chaotic")
        >>> print(f"Loaded {len(chaotic_data)} tickets")
    """
    file_path = TEST_DATA_DIR / f"scenario_{scenario_name}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {file_path}\n"
            f"Available scenarios: {list_available_scenarios()}"
        )

    logger.info(f"Loading test scenario: {scenario_name} from {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Successfully loaded {len(data)} tickets from '{scenario_name}' scenario")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise


def load_all_scenarios() -> Dict[str, List[Dict]]:
    """
    Load all available test scenarios.

    Returns:
        Dictionary mapping scenario names to ticket lists

    Example:
        >>> all_data = load_all_scenarios()
        >>> print(all_data.keys())
        dict_keys(['chaotic', 'healthy', 'extreme', 'edge_cases', 'empty', 'single'])
    """
    scenarios = {
        "chaotic": "chaotic",
        "healthy": "healthy",
        "extreme": "extreme",
        "edge_cases": "edge_cases",
        "empty": "empty",
        "single": "single"
    }

    loaded = {}
    for name, filename in scenarios.items():
        try:
            loaded[name] = load_scenario(filename)
            logger.info(f"Loaded scenario '{name}': {len(loaded[name])} tickets")
        except FileNotFoundError:
            logger.warning(f"Scenario '{name}' not found, skipping")
        except Exception as e:
            logger.error(f"Error loading scenario '{name}': {e}")

    return loaded


def list_available_scenarios() -> List[str]:
    """
    List all available scenario files in test_data directory.

    Returns:
        List of scenario names (without 'scenario_' prefix and '.json' suffix)

    Example:
        >>> scenarios = list_available_scenarios()
        >>> print(scenarios)
        ['chaotic', 'healthy', 'extreme', 'edge_cases', 'empty', 'single']
    """
    if not TEST_DATA_DIR.exists():
        logger.warning(f"Test data directory not found: {TEST_DATA_DIR}")
        return []

    scenario_files = TEST_DATA_DIR.glob("scenario_*.json")
    scenarios = [
        f.stem.replace("scenario_", "")
        for f in scenario_files
    ]

    return sorted(scenarios)


def get_scenario_stats(scenario_name: str) -> Dict[str, any]:
    """
    Get statistics about a test scenario.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Dictionary with scenario statistics

    Example:
        >>> stats = get_scenario_stats("chaotic")
        >>> print(stats)
        {
            'name': 'chaotic',
            'total_tickets': 6,
            'sources': ['Jira', 'Salesforce', 'ServiceNow', 'Zendesk', 'Datadog', 'PagerDuty'],
            'priorities': {'Critical': 2, 'High': 2, 'Medium': 1, 'Low': 1},
            'statuses': {'Open': 4, 'Closed': 1, 'Pending Vendor': 1, 'Resolved': 1},
            'duplicate_ids': ['TKT-101', 'TKT-108']
        }
    """
    data = load_scenario(scenario_name)

    # Count by source
    sources = list(set(ticket['source'] for ticket in data))

    # Count by priority
    priorities = {}
    for ticket in data:
        priority = ticket['priority']
        priorities[priority] = priorities.get(priority, 0) + 1

    # Count by status
    statuses = {}
    for ticket in data:
        status = ticket['status']
        statuses[status] = statuses.get(status, 0) + 1

    # Find duplicate IDs
    ticket_ids = [ticket['id'] for ticket in data]
    duplicate_ids = list(set([tid for tid in ticket_ids if ticket_ids.count(tid) > 1]))

    stats = {
        'name': scenario_name,
        'total_tickets': len(data),
        'sources': sorted(sources),
        'priorities': priorities,
        'statuses': statuses,
        'duplicate_ids': duplicate_ids if duplicate_ids else None
    }

    return stats


def print_scenario_summary(scenario_name: str):
    """
    Print a formatted summary of a test scenario.

    Args:
        scenario_name: Name of the scenario

    Example:
        >>> print_scenario_summary("chaotic")
        ===== Scenario: chaotic =====
        Total Tickets: 6
        Sources: Datadog, Jira, PagerDuty, Salesforce, ServiceNow, Zendesk
        Priorities: Critical (2), High (2), Low (1), Medium (1)
        Statuses: Closed (1), Open (4), Pending Vendor (1), Resolved (1)
        Duplicate IDs: TKT-101, TKT-108
    """
    stats = get_scenario_stats(scenario_name)

    print(f"\n===== Scenario: {scenario_name} =====")
    print(f"Total Tickets: {stats['total_tickets']}")
    print(f"Sources: {', '.join(stats['sources'])}")

    priorities_str = ', '.join([f"{k} ({v})" for k, v in stats['priorities'].items()])
    print(f"Priorities: {priorities_str}")

    statuses_str = ', '.join([f"{k} ({v})" for k, v in stats['statuses'].items()])
    print(f"Statuses: {statuses_str}")

    if stats['duplicate_ids']:
        print(f"Duplicate IDs: {', '.join(stats['duplicate_ids'])}")
    else:
        print("Duplicate IDs: None")

    print("=" * (len(scenario_name) + 20))


# Convenience functions for specific scenarios
def load_chaotic() -> List[Dict]:
    """Load the chaotic test scenario (primary test data)."""
    return load_scenario("chaotic")


def load_healthy() -> List[Dict]:
    """Load the healthy test scenario (conflict-free data)."""
    return load_scenario("healthy")


def load_extreme() -> List[Dict]:
    """Load the extreme test scenario (stress test data)."""
    return load_scenario("extreme")


def load_edge_cases() -> List[Dict]:
    """Load the edge cases test scenario."""
    return load_scenario("edge_cases")


def load_empty() -> List[Dict]:
    """Load the empty test scenario (empty array)."""
    return load_scenario("empty")


def load_single() -> List[Dict]:
    """Load the single ticket test scenario."""
    return load_scenario("single")


if __name__ == "__main__":
    # Demo usage
    print("Test Data Loader - Available Scenarios:")
    print("-" * 40)

    available = list_available_scenarios()
    print(f"Found {len(available)} scenarios: {', '.join(available)}\n")

    for scenario in available:
        try:
            print_scenario_summary(scenario)
        except Exception as e:
            print(f"Error loading {scenario}: {e}")
