"""
Test Chat Agent - ASK Mode Q&A Testing

Tests all 15 ASK mode questions from chat_scenarios.md
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.chat_agent import chat_agent

# Import test data loader
sys.path.insert(0, str(Path(__file__).parent.parent))
from test_data.loader import load_test_scenario, get_test_stats


# Test questions from chat_scenarios.md
ASK_MODE_QUESTIONS = [
    # Basic Information Queries
    {
        "id": 1,
        "question": "What tickets are overdue?",
        "category": "Basic Information",
        "expected_keywords": ["TKT-99", "overdue", "5 days"],
        "expected_tickets": ["TKT-99", "TKT-112"]
    },
    {
        "id": 2,
        "question": "Tell me about TKT-101",
        "category": "Basic Information",
        "expected_keywords": ["TKT-101", "conflict", "Salesforce", "ServiceNow"],
        "expected_tickets": ["TKT-101"]
    },
    {
        "id": 3,
        "question": "What's the status of TKT-108?",
        "category": "Basic Information",
        "expected_keywords": ["TKT-108", "conflict", "Datadog", "PagerDuty"],
        "expected_tickets": ["TKT-108"]
    },
    {
        "id": 4,
        "question": "Show me all tickets from Acme Corp",
        "category": "Basic Information",
        "expected_keywords": ["Acme Corp", "TKT-99"],
        "expected_tickets": ["TKT-99"]
    },
    {
        "id": 5,
        "question": "List all Jira tickets",
        "category": "Basic Information",
        "expected_keywords": ["Jira"],
        "expected_tickets": []  # Will depend on test data
    },

    # Analytical Queries
    {
        "id": 6,
        "question": "What should I prioritize today?",
        "category": "Analytical",
        "expected_keywords": ["TKT-99", "critical", "overdue"],
        "expected_tickets": ["TKT-99", "TKT-108", "TKT-112"]
    },
    {
        "id": 7,
        "question": "Why is there a conflict in ticket 101?",
        "category": "Analytical",
        "expected_keywords": ["TKT-101", "conflict", "sync", "Salesforce", "ServiceNow"],
        "expected_tickets": ["TKT-101"]
    },
    {
        "id": 8,
        "question": "Are there any critical priority items?",
        "category": "Analytical",
        "expected_keywords": ["critical", "TKT-99"],
        "expected_tickets": ["TKT-99", "TKT-108"]
    },
    {
        "id": 9,
        "question": "Which tickets are assigned to Sarah Connor?",
        "category": "Analytical",
        "expected_keywords": ["Sarah Connor", "TKT-101"],
        "expected_tickets": ["TKT-101"]
    },
    {
        "id": 10,
        "question": "How many tickets are currently open?",
        "category": "Analytical",
        "expected_keywords": ["open", "ticket"],
        "expected_tickets": []
    },

    # Pattern Recognition
    {
        "id": 11,
        "question": "Are there any duplicate tickets?",
        "category": "Pattern Recognition",
        "expected_keywords": ["duplicate", "TKT-101", "TKT-108"],
        "expected_tickets": ["TKT-101", "TKT-108"]
    },
    {
        "id": 12,
        "question": "What data conflicts exist in the system?",
        "category": "Pattern Recognition",
        "expected_keywords": ["conflict", "TKT-101", "TKT-108"],
        "expected_tickets": ["TKT-101", "TKT-108"]
    },
    {
        "id": 13,
        "question": "Which tickets are approaching their due date?",
        "category": "Pattern Recognition",
        "expected_keywords": ["due", "TKT-112"],
        "expected_tickets": ["TKT-112"]
    },
    {
        "id": 14,
        "question": "What's the overall health of the system?",
        "category": "Pattern Recognition",
        "expected_keywords": ["health", "system", "ticket"],
        "expected_tickets": []
    },
    {
        "id": 15,
        "question": "Which customers have the most urgent issues?",
        "category": "Pattern Recognition",
        "expected_keywords": ["Acme Corp", "urgent", "critical"],
        "expected_tickets": ["TKT-99"]
    }
]


# Multi-turn conversation scenarios
CONVERSATION_SCENARIOS = [
    {
        "name": "Troubleshooting Flow",
        "turns": [
            {
                "role": "user",
                "content": "What's the status of TKT-101?",
                "expected_keywords": ["TKT-101", "conflict"]
            },
            {
                "role": "user",
                "content": "Why is there a conflict?",
                "expected_keywords": ["sync", "Salesforce", "ServiceNow"]
            },
            {
                "role": "user",
                "content": "What should I do?",
                "expected_keywords": ["action", "sync", "update"]
            }
        ]
    },
    {
        "name": "Prioritization Flow",
        "turns": [
            {
                "role": "user",
                "content": "What should I prioritize today?",
                "expected_keywords": ["TKT-99", "critical"]
            },
            {
                "role": "user",
                "content": "Tell me more about the first one",
                "expected_keywords": ["TKT-99", "Acme Corp", "overdue"]
            }
        ]
    },
    {
        "name": "Context Awareness Flow",
        "turns": [
            {
                "role": "user",
                "content": "Are there any SLA breaches?",
                "expected_keywords": ["TKT-99", "breach"]
            },
            {
                "role": "user",
                "content": "What's the customer for the critical one?",
                "expected_keywords": ["Acme Corp"]
            }
        ]
    }
]


async def test_single_question(question_data: dict, context: dict) -> dict:
    """Test a single ASK mode question."""

    question = question_data["question"]
    print(f"\n{'='*80}")
    print(f"Q{question_data['id']}: {question}")
    print(f"Category: {question_data['category']}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        # Send question to chat agent
        response = await chat_agent.chat(
            message=question,
            history=[],
            context=context
        )

        duration = time.time() - start_time

        # Check for expected keywords
        keywords_found = []
        keywords_missing = []
        for keyword in question_data["expected_keywords"]:
            if keyword.lower() in response.lower():
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)

        # Check for expected tickets
        tickets_found = []
        tickets_missing = []
        for ticket in question_data["expected_tickets"]:
            if ticket in response:
                tickets_found.append(ticket)
            else:
                tickets_missing.append(ticket)

        # Determine if test passed
        passed = len(keywords_missing) == 0 or len(keywords_found) >= len(question_data["expected_keywords"]) / 2

        # Print results
        print(f"\n📝 RESPONSE ({duration:.2f}s):")
        print(f"{response}\n")

        print(f"✅ Keywords Found: {', '.join(keywords_found) if keywords_found else 'None'}")
        if keywords_missing:
            print(f"⚠️  Keywords Missing: {', '.join(keywords_missing)}")

        if question_data["expected_tickets"]:
            print(f"🎫 Tickets Found: {', '.join(tickets_found) if tickets_found else 'None'}")
            if tickets_missing:
                print(f"⚠️  Tickets Missing: {', '.join(tickets_missing)}")

        print(f"\n{'✅ PASSED' if passed else '❌ FAILED'}")

        return {
            "id": question_data["id"],
            "question": question,
            "category": question_data["category"],
            "response": response,
            "duration": duration,
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "tickets_found": tickets_found,
            "tickets_missing": tickets_missing,
            "passed": passed
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ ERROR ({duration:.2f}s): {str(e)}")

        return {
            "id": question_data["id"],
            "question": question,
            "category": question_data["category"],
            "error": str(e),
            "duration": duration,
            "passed": False
        }


async def test_conversation(scenario: dict, context: dict) -> dict:
    """Test a multi-turn conversation scenario."""

    print(f"\n{'='*80}")
    print(f"💬 CONVERSATION: {scenario['name']}")
    print(f"{'='*80}")

    history = []
    results = []
    total_duration = 0

    for i, turn in enumerate(scenario["turns"], 1):
        print(f"\n--- Turn {i} ---")
        print(f"USER: {turn['content']}")

        start_time = time.time()

        try:
            response = await chat_agent.chat(
                message=turn["content"],
                history=history,
                context=context
            )

            duration = time.time() - start_time
            total_duration += duration

            print(f"AGENT ({duration:.2f}s): {response}")

            # Update history
            history.append({"role": "user", "content": turn["content"]})
            history.append({"role": "assistant", "content": response})

            # Check expected keywords
            keywords_found = [kw for kw in turn.get("expected_keywords", []) if kw.lower() in response.lower()]
            keywords_missing = [kw for kw in turn.get("expected_keywords", []) if kw.lower() not in response.lower()]

            if keywords_found:
                print(f"✅ Keywords: {', '.join(keywords_found)}")
            if keywords_missing:
                print(f"⚠️  Missing: {', '.join(keywords_missing)}")

            results.append({
                "turn": i,
                "user_message": turn["content"],
                "agent_response": response,
                "duration": duration,
                "keywords_found": keywords_found,
                "keywords_missing": keywords_missing
            })

        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ ERROR ({duration:.2f}s): {str(e)}")
            results.append({
                "turn": i,
                "error": str(e),
                "duration": duration
            })
            break

    passed = all("error" not in r for r in results)

    print(f"\n{'✅ CONVERSATION PASSED' if passed else '❌ CONVERSATION FAILED'}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")

    return {
        "name": scenario["name"],
        "turns": results,
        "total_duration": total_duration,
        "passed": passed
    }


async def run_all_tests():
    """Run all chat agent tests."""

    print("\n" + "="*80)
    print("🧪 CHAT AGENT TEST SUITE - ASK MODE Q&A")
    print("="*80)

    # Load test data
    print("\n📊 Loading test data...")
    chaotic_data = load_test_scenario("chaotic")
    stats = get_test_stats(chaotic_data)

    print(f"\n✅ Loaded {stats['total_tickets']} tickets")
    print(f"   - {stats['total_sources']} sources: {', '.join(stats['sources'])}")
    print(f"   - {stats['duplicate_tickets']} duplicate tickets")
    print(f"   - {stats['conflicting_tickets']} tickets with conflicts")

    # Prepare context
    context = {
        "data": chaotic_data,
        "briefing": {}  # Could load briefing here for full context
    }

    # Test individual questions
    print("\n" + "="*80)
    print("📝 TESTING INDIVIDUAL QUESTIONS")
    print("="*80)

    question_results = []
    for question_data in ASK_MODE_QUESTIONS:
        result = await test_single_question(question_data, context)
        question_results.append(result)
        await asyncio.sleep(0.5)  # Small delay between requests

    # Test conversations
    print("\n" + "="*80)
    print("💬 TESTING MULTI-TURN CONVERSATIONS")
    print("="*80)

    conversation_results = []
    for scenario in CONVERSATION_SCENARIOS:
        result = await test_conversation(scenario, context)
        conversation_results.append(result)
        await asyncio.sleep(0.5)

    # Generate summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    # Question results
    total_questions = len(question_results)
    passed_questions = sum(1 for r in question_results if r.get("passed", False))
    failed_questions = total_questions - passed_questions

    print(f"\n📝 INDIVIDUAL QUESTIONS:")
    print(f"   Total: {total_questions}")
    print(f"   ✅ Passed: {passed_questions}")
    print(f"   ❌ Failed: {failed_questions}")
    print(f"   Success Rate: {(passed_questions/total_questions*100):.1f}%")

    # Category breakdown
    print(f"\n📊 BY CATEGORY:")
    categories = {}
    for result in question_results:
        cat = result.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if result.get("passed", False):
            categories[cat]["passed"] += 1

    for cat, stats in categories.items():
        print(f"   {cat}: {stats['passed']}/{stats['total']} ({stats['passed']/stats['total']*100:.0f}%)")

    # Conversation results
    total_convs = len(conversation_results)
    passed_convs = sum(1 for r in conversation_results if r.get("passed", False))

    print(f"\n💬 CONVERSATIONS:")
    print(f"   Total: {total_convs}")
    print(f"   ✅ Passed: {passed_convs}")
    print(f"   ❌ Failed: {total_convs - passed_convs}")

    # Performance stats
    all_durations = [r.get("duration", 0) for r in question_results if "duration" in r]
    if all_durations:
        print(f"\n⏱️  PERFORMANCE:")
        print(f"   Average Response Time: {sum(all_durations)/len(all_durations):.2f}s")
        print(f"   Min: {min(all_durations):.2f}s")
        print(f"   Max: {max(all_durations):.2f}s")

    # Failed tests detail
    if failed_questions > 0:
        print(f"\n❌ FAILED TESTS:")
        for result in question_results:
            if not result.get("passed", False):
                print(f"   Q{result['id']}: {result['question']}")
                if "error" in result:
                    print(f"      Error: {result['error']}")
                elif result.get("keywords_missing"):
                    print(f"      Missing keywords: {', '.join(result['keywords_missing'])}")

    print("\n" + "="*80)
    print("✅ CHAT AGENT TEST SUITE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
