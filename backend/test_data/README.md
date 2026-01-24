# Test Data Directory

This directory contains **dummy test data** for Phase 2 agent testing. All data files here are **temporary** and will be replaced with real data connectors in Phase 3+.

---

## ⚠️ Important Notice

**These are NOT production data sources!**

All JSON files in this directory are static test scenarios designed to validate agent functionality. When moving to production:
- Replace with live API connectors (ServiceNow, Salesforce, Jira, etc.)
- See `DATA_SOURCE_MIGRATION.md` in the backend directory for migration guide

---

## Test Scenario Files

### 1. `scenario_chaotic.json`
**Purpose**: Primary test scenario with intentional data issues

**Contents**: 6 tickets (based on frontend RAW_CHAOTIC_DATA)
- **TKT-99**: Critical SLA breach (5 days overdue) from Jira
- **TKT-101**: Data conflict - Closed (Salesforce) vs Pending Vendor (ServiceNow)
- **TKT-105**: Normal low-priority password reset (Zendesk) - healthy ticket
- **TKT-108**: Priority and status conflict - Resolved/Medium (Datadog) vs Open/Critical (PagerDuty)
- **TKT-112**: Approaching breach (due today) from ServiceNow

**Key Chaos Elements**:
- 1 critical SLA breach (TKT-99)
- 2 data conflicts with duplicate IDs (TKT-101, TKT-108)
- 1 approaching breach (TKT-112)
- Mix of 6 different data sources

**Expected Briefing Agent Behavior**:
- Identify TKT-99 as critical SLA breach
- Detect TKT-101 status conflict
- Detect TKT-108 status and priority conflict
- Flag TKT-112 as approaching due date
- Ignore TKT-105 (healthy ticket)

**Use For**:
- Primary briefing agent testing
- Chat agent context testing
- Action agent decision-making

---

### 2. `scenario_healthy.json`
**Purpose**: Test agent behavior with clean, conflict-free data

**Contents**: 6 tickets with no issues
- All tickets have future due dates or properly closed
- No duplicate IDs
- No conflicting statuses or priorities
- Mix of different sources and priorities

**Expected Briefing Agent Behavior**:
- Return "all clear" or minimal summary
- Empty or near-empty items list
- No false positives

**Use For**:
- Testing agent's ability to report healthy systems
- Validating no false positives in conflict detection
- Baseline performance benchmarking

---

### 3. `scenario_extreme.json`
**Purpose**: Stress test with multiple simultaneous critical issues

**Contents**: 13 tickets with severe problems
- 5 critical SLA breaches (300, 301, 302, 305, 307)
- 3 data conflicts (303, 304, 308 - duplicates with differing statuses)
- Multiple critical priority items
- 10+ days overdue tickets

**Key Test Elements**:
- Multiple SLA breaches at different severity levels
- Several data conflicts across systems
- Mix of critical, high, and medium priorities
- Tests agent's prioritization logic
- Tests handling of large issue lists

**Expected Briefing Agent Behavior**:
- Prioritize most critical SLA breaches first
- Group related conflicts together
- Provide clear severity ordering
- Handle large number of items gracefully

**Use For**:
- Stress testing agent capacity
- Testing prioritization algorithms
- Validating performance with complex datasets

---

### 4. `scenario_edge_cases.json`
**Purpose**: Test edge case handling

**Contents**: 3 tickets, all from same source (Jira), all same priority (Critical)
- All tickets from single source only
- All identical priority level
- Tests agent's behavior with homogeneous data

**Expected Briefing Agent Behavior**:
- Handle single-source dataset correctly
- No errors from lack of diversity
- Sensible analysis despite uniformity

**Use For**:
- Testing single-source data handling
- Validating uniform priority handling
- Edge case validation

---

### 5. `scenario_empty.json`
**Purpose**: Test empty dataset handling

**Contents**: Empty array `[]`

**Expected Briefing Agent Behavior**:
- Graceful handling without crashes
- Return "no data available" or similar message
- Proper error handling

**Use For**:
- Error handling validation
- Empty state testing
- Defensive coding verification

---

### 6. `scenario_single.json`
**Purpose**: Test single ticket handling

**Contents**: 1 ticket (TKT-999)
- Single healthy ticket
- No issues, future due date

**Expected Briefing Agent Behavior**:
- Process single ticket correctly
- No errors from minimal dataset
- Appropriate summary for single item

**Use For**:
- Minimum dataset testing
- Single-item processing validation

---

## Chat Scenarios

### `chat_scenarios.md`
Comprehensive list of test questions and commands for Chat and Action agents:

**ASK Mode Questions (15)**:
- Basic information queries
- Analytical queries
- Pattern recognition questions
- Multi-turn conversation scenarios

**DO Mode Commands (10)**:
- Ticket status updates
- Notification sending
- Automation triggers
- Multi-step actions

**Safety Tests**:
- Bulk operations requiring confirmation
- Invalid inputs
- Edge case commands

See file for complete details and expected behaviors.

---

## File Structure

```
backend/test_data/
├── README.md                      # This file
├── scenario_chaotic.json          # Primary test scenario (6 tickets)
├── scenario_healthy.json          # Clean data scenario (6 tickets)
├── scenario_extreme.json          # Stress test scenario (13 tickets)
├── scenario_edge_cases.json       # Edge case scenario (3 tickets)
├── scenario_empty.json            # Empty dataset ([])
├── scenario_single.json           # Single ticket scenario
└── chat_scenarios.md              # Q&A and command test scenarios
```

---

## Usage in Tests

### Loading Test Data

```python
import json
from pathlib import Path

# Load specific scenario
def load_scenario(name: str):
    with open(f"test_data/scenario_{name}.json") as f:
        return json.load(f)

chaotic_data = load_scenario("chaotic")
healthy_data = load_scenario("healthy")
extreme_data = load_scenario("extreme")
```

### Using with Agents

```python
from app.agents.briefing_agent import briefing_agent

# Test with chaotic data
result = await briefing_agent.analyze_data(chaotic_data)
print(f"Summary: {result['summary']}")
print(f"Items Found: {len(result['items'])}")

# Test with healthy data
result = await briefing_agent.analyze_data(healthy_data)
print(f"Summary: {result['summary']}")
# Expected: Minimal or no items
```

### API Testing

```bash
# Test briefing endpoint with chaotic data
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d @test_data/scenario_chaotic.json

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tickets are overdue?",
    "history": [],
    "mode": "ASK",
    "context": {"data": [...]}
  }'
```

---

## Test Coverage Matrix

| Scenario | SLA Breaches | Data Conflicts | Healthy Tickets | Total Tickets |
|----------|--------------|----------------|-----------------|---------------|
| Chaotic  | 2 | 2 | 1 | 6 |
| Healthy  | 0 | 0 | 6 | 6 |
| Extreme  | 5 | 3 | 0 | 13 |
| Edge Cases | 0 | 0 | 3 | 3 |
| Empty    | 0 | 0 | 0 | 0 |
| Single   | 0 | 0 | 1 | 1 |

---

## Expected Agent Behaviors by Scenario

### Briefing Agent

| Scenario | Expected Items | Expected Summary |
|----------|----------------|------------------|
| Chaotic  | 3-4 items | Critical issues detected |
| Healthy  | 0-1 items | System healthy / All clear |
| Extreme  | 8-10 items | Multiple critical issues |
| Edge Cases | 0 items | Single-source data note |
| Empty    | 0 items | No data available |
| Single   | 0-1 items | Single ticket summary |

### Chat Agent

| Question Type | Test Scenario | Expected Behavior |
|---------------|---------------|-------------------|
| "What tickets are overdue?" | Chaotic | Mention TKT-99, TKT-112 |
| "Tell me about TKT-101" | Chaotic | Explain data conflict |
| "What should I prioritize?" | Extreme | List multiple critical items |
| "Show all Jira tickets" | Edge Cases | Return all 3 tickets |
| "Are there any issues?" | Healthy | Report "no issues" or "all clear" |
| "What tickets exist?" | Empty | "No tickets found" |

### Action Agent

| Command Type | Expected Tool | Expected Response |
|--------------|---------------|-------------------|
| "Update TKT-99 status..." | update_ticket_status | Confirmation with details |
| "Send notification to..." | send_notification | Notification sent confirmation |
| "Trigger automation..." | trigger_automation | Automation initiated |
| "Delete all tickets" | NONE | Refusal or request confirmation |

---

## Adding New Test Scenarios

To add a new test scenario:

1. Create `scenario_[name].json` following the Ticket model structure
2. Document it in this README under "Test Scenario Files"
3. Update the Test Coverage Matrix
4. Add expected behaviors to the tables
5. Create corresponding test cases in test scripts

**Ticket Model Structure**:
```json
{
  "id": "TKT-XXX",
  "customer": "Company Name",
  "title": "Issue Description",
  "status": "Open|In Progress|Resolved|Closed|Pending Vendor",
  "priority": "Critical|High|Medium|Low",
  "createdDate": "YYYY-MM-DD",
  "dueDate": "YYYY-MM-DD",
  "source": "Jira|ServiceNow|Salesforce|Zendesk|Datadog|PagerDuty",
  "assignee": "Person Name or Unassigned"
}
```

---

## Maintenance

**Review Dates**:
- Last Updated: 2026-01-24 (Phase 2 start)
- Next Review: When starting Phase 3 (real data connectors)

**Deprecation Notice**:
These files will be **archived or removed** once real data connectors are implemented in Phase 3+. Do not use these for production testing beyond Phase 2.

---

## Related Documentation

- [../DATA_SOURCE_MIGRATION.md](../DATA_SOURCE_MIGRATION.md) - Guide for replacing dummy data with real connectors
- [chat_scenarios.md](./chat_scenarios.md) - Detailed Q&A and command test scenarios
- [../PHASE2_TEST_RESULTS.md](../PHASE2_TEST_RESULTS.md) - Test execution results (created after testing)

---

*Test data created: 2026-01-24*
*For Phase 2 testing only - temporary data*
