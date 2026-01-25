"""
API Endpoint Integration Tests

Tests all FastAPI endpoints with real HTTP requests.
"""

import requests
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from test_data.loader import load_test_scenario

# API base URL
API_BASE_URL = "http://localhost:8000"


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"🧪 {title}")
    print("="*80)


def test_root_endpoint():
    """Test the root endpoint."""
    print_header("Testing Root Endpoint")

    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        assert response.status_code == 200
        assert response.json()["status"] == "online"
        print("✅ PASS: Root endpoint working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def test_health_endpoint():
    """Test the health check endpoint."""
    print_header("Testing Health Check Endpoint")

    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ PASS: Health endpoint working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def test_briefing_endpoint():
    """Test the briefing endpoint."""
    print_header("Testing Briefing Endpoint")

    try:
        # Load test data
        chaotic_data = load_test_scenario("chaotic")

        # Make request
        payload = {"data": chaotic_data}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/briefing",
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        result = response.json()
        print(f"\nSummary: {result['summary']}")
        print(f"Items Found: {len(result['items'])}")

        for item in result['items']:
            print(f"\n  [{item['severity']}] {item['type']}: {item['title']}")
            print(f"    Related Tickets: {', '.join(item['relatedTicketIds'])}")
            if item.get('suggestedAction'):
                print(f"    Action: {item['suggestedAction']}")

        assert response.status_code == 200
        assert "summary" in result
        assert "items" in result
        assert isinstance(result["items"], list)

        print("\n✅ PASS: Briefing endpoint working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_ask_mode():
    """Test the chat endpoint in ASK mode."""
    print_header("Testing Chat Endpoint (ASK Mode)")

    try:
        # Load test data
        chaotic_data = load_test_scenario("chaotic")

        # Test questions
        questions = [
            "What tickets are overdue?",
            "Tell me about TKT-101",
            "What should I prioritize today?"
        ]

        for question in questions:
            print(f"\n📝 Question: {question}")

            payload = {
                "message": question,
                "history": [],
                "mode": "ASK",
                "context": {"data": chaotic_data}
            }

            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                timeout=30
            )

            result = response.json()
            print(f"Response: {result['response'][:200]}...")

            assert response.status_code == 200
            assert "response" in result
            assert "timestamp" in result

        print("\n✅ PASS: Chat ASK mode working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_do_mode():
    """Test the chat endpoint in DO mode."""
    print_header("Testing Chat Endpoint (DO Mode)")

    try:
        # Load test data
        chaotic_data = load_test_scenario("chaotic")

        # Test commands
        commands = [
            "Update TKT-99 status to In Progress",
            "Send notification to DevOps Team about TKT-99",
            "Trigger escalation automation for critical tickets"
        ]

        for command in commands:
            print(f"\n⚡ Command: {command}")

            payload = {
                "message": command,
                "history": [],
                "mode": "DO",
                "context": {"data": chaotic_data}
            }

            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                timeout=30
            )

            result = response.json()
            print(f"Response: {result['response'][:200]}...")

            assert response.status_code == 200
            assert "response" in result
            assert "timestamp" in result

        print("\n✅ PASS: Chat DO mode working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling with invalid requests."""
    print_header("Testing Error Handling")

    try:
        # Test invalid briefing request (missing data field)
        print("\n📝 Testing invalid briefing request...")
        response = requests.post(
            f"{API_BASE_URL}/api/v1/briefing",
            json={"invalid": "data"},
            timeout=10
        )
        print(f"Status: {response.status_code} (expected 422)")
        assert response.status_code == 422

        # Test invalid chat request (missing required fields)
        print("\n📝 Testing invalid chat request...")
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat",
            json={"message": "test"},  # Missing history and mode
            timeout=10
        )
        print(f"Status: {response.status_code} (expected 422)")
        assert response.status_code == 422

        print("\n✅ PASS: Error handling working")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def run_all_tests():
    """Run all API endpoint tests."""
    print("\n" + "="*80)
    print("🚀 X360 AI AGENT - API ENDPOINT TEST SUITE")
    print("="*80)

    print(f"\nTesting API at: {API_BASE_URL}")
    print("Make sure the FastAPI server is running!")

    # Check if server is running
    try:
        requests.get(API_BASE_URL, timeout=2)
    except Exception:
        print("\n❌ ERROR: API server not running!")
        print("Start the server with: uvicorn app.main:app --reload")
        return

    # Run tests
    results = {
        "Root Endpoint": test_root_endpoint(),
        "Health Check": test_health_endpoint(),
        "Briefing Endpoint": test_briefing_endpoint(),
        "Chat ASK Mode": test_chat_ask_mode(),
        "Chat DO Mode": test_chat_do_mode(),
        "Error Handling": test_error_handling()
    }

    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{'='*80}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80 + "\n")

    if passed == total:
        print("✅ ALL TESTS PASSED - API is ready for frontend integration!")
    else:
        print("⚠️  Some tests failed - please review the errors above")


if __name__ == "__main__":
    run_all_tests()
