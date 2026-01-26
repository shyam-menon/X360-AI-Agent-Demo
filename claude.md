**Strands AWS Knowledge Base Retrieval**

- Purpose: Use the Strands `retrieve` tool to query Amazon Bedrock Knowledge Bases from a Strands Agent session.
- Source: https://github.com/strands-agents/tools/blob/main/src/strands_tools/retrieve.py

**Prereqs**
- AWS credentials available to the runtime (default profile or a named profile). Verify with `aws sts get-caller-identity`.
- Amazon Bedrock Knowledge Base deployed and accessible; note its `knowledgeBaseId` and region.
- Optional env defaults (fallbacks used if not passed in the call):
  - `KNOWLEDGE_BASE_ID` — default KB ID
  - `AWS_REGION` — default region (code defaults to `us-west-2`)
  - `MIN_SCORE` — minimum relevance score (default `0.4`)
  - `RETRIEVE_ENABLE_METADATA_DEFAULT` — `true|false` to include metadata by default

**Basic usage**

```python
from strands import Agent
from strands_tools import retrieve

agent = Agent(tools=[retrieve])

# Minimal call (uses env defaults for KB ID/region)
resp = agent.tool.retrieve(text="What is the STRANDS SDK?")
print(resp)

# Explicit configuration
resp = agent.tool.retrieve(
	text="deployment steps for production",
	numberOfResults=5,          # max results (default 10)
	score=0.7,                  # min relevance score (0.0-1.0, default 0.4)
	knowledgeBaseId="kb-123",  # overrides KNOWLEDGE_BASE_ID
	region="us-east-1",        # overrides AWS_REGION
	enableMetadata=True,        # include source/chunk metadata in output
	profile_name="prod",       # use a named AWS profile (optional)
)
print(resp)
```

**Filtering with `retrieveFilter`**
- Structure mirrors Bedrock KB metadata filters; only one top-level operator is allowed.
- Supported operators: `equals`, `notEquals`, `greaterThan`, `greaterThanOrEquals`, `lessThan`, `lessThanOrEquals`, `in`, `notIn`, `listContains`, `stringContains`, `startsWith` (OpenSearch Serverless), `andAll`, `orAll`.
- Example:

```python
resp = agent.tool.retrieve(
	text="security controls",
	retrieveFilter={
		"andAll": [
			{"equals": {"key": "category", "value": "security"}},
			{"greaterThan": {"key": "year", "value": "2022"}},
		]
	},
)
```

**Result format**
- Returns dict with `status` and `content` containing formatted text. Results are filtered by `score` before formatting.
- When metadata is enabled, includes source URI, chunk ID, and data source ID where present.

**Troubleshooting**
- Ensure the KB ID matches the region you query.
- If using `profile_name`, the profile must exist in `~/.aws/credentials`.
- Errors like “Invalid operator” come from `retrieveFilter` validation—check operator names and value shapes.
