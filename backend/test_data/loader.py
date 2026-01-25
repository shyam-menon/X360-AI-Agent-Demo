"""
Test Data Loader - Utility for loading test scenarios
"""

import json
from pathlib import Path
from typing import List, Dict, Any


TEST_DATA_DIR = Path(__file__).parent


def load_test_scenario(scenario_name: str) -> List[Dict[str, Any]]:
    """
    Load a test scenario by name.

    Args:
        scenario_name: Name of scenario (e.g., 'chaotic', 'healthy', 'extreme')

    Returns:
        List of ticket dictionaries
    """
    scenario_file = TEST_DATA_DIR / f"scenario_{scenario_name}.json"

    if not scenario_file.exists():
        raise FileNotFoundError(f"Scenario file not found: {scenario_file}")

    with open(scenario_file, 'r') as f:
        return json.load(f)


def get_test_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for test data.

    Args:
        data: List of ticket dictionaries

    Returns:
        Dictionary with statistics
    """
    if not data:
        return {
            "total_tickets": 0,
            "total_sources": 0,
            "sources": [],
            "duplicate_tickets": 0,
            "conflicting_tickets": 0,
            "overdue_tickets": 0,
            "critical_tickets": 0
        }

    # Count tickets by source
    sources = set()
    ticket_ids = {}

    for ticket in data:
        source = ticket.get("source", "Unknown")
        sources.add(source)

        # Track duplicates
        ticket_id = ticket.get("id")
        if ticket_id:
            if ticket_id in ticket_ids:
                ticket_ids[ticket_id] += 1
            else:
                ticket_ids[ticket_id] = 1

    # Count duplicates and conflicts
    duplicate_tickets = sum(1 for count in ticket_ids.values() if count > 1)
    conflicting_tickets = duplicate_tickets  # Simplification

    # Count overdue and critical
    overdue_tickets = sum(1 for t in data if "overdue" in str(t).lower())
    critical_tickets = sum(1 for t in data if t.get("priority") == "Critical")

    return {
        "total_tickets": len(data),
        "total_sources": len(sources),
        "sources": sorted(list(sources)),
        "duplicate_tickets": duplicate_tickets,
        "conflicting_tickets": conflicting_tickets,
        "overdue_tickets": overdue_tickets,
        "critical_tickets": critical_tickets
    }


def list_scenarios() -> List[str]:
    """
    List all available test scenarios.

    Returns:
        List of scenario names
    """
    scenario_files = list(TEST_DATA_DIR.glob("scenario_*.json"))
    return [f.stem.replace("scenario_", "") for f in scenario_files]
