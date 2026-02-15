# marktools

> **The SDK that lets AI agents buy pre-solved reasoning workflows.**

[![PyPI](https://img.shields.io/pypi/v/marktools.svg)](https://pypi.org/project/marktools/)
[![Python](https://img.shields.io/pypi/pyversions/marktools.svg)](https://pypi.org/project/marktools/)
[![License](https://img.shields.io/pypi/l/marktools.svg)](https://github.com/akhaire21/treehacks-2026/blob/main/LICENSE)

**marktools** gives your AI agents access to a marketplace of expert-crafted, pre-solved reasoning workflows. Instead of spending thousands of tokens figuring out how to file Ohio taxes or plan a multi-city trip from scratch, your agent calls `mark.estimate()`, gets a price quote, and buys a battle-tested solution — complete with step-by-step instructions, edge cases, and domain knowledge.

## Quick Start

```bash
pip install marktools
```

### 3 Lines to Supercharge Any Agent

```python
from marktools import MarkClient

mark = MarkClient(api_key="mk_...")  # or set MARK_API_KEY env var

# 1. Estimate — is the marketplace worth it? (free, no credits)
estimate = mark.estimate("File Ohio 2024 taxes with W2 and itemized deductions")

# 2. Buy — purchase the best solution
receipt = mark.buy(estimate.session_id, estimate.best_solution.solution_id)

# 3. Use — step-by-step instructions, edge cases, domain knowledge
for wf in receipt.execution_plan.workflows:
    print(f"📋 {wf.workflow_title}")
    for step in wf.workflow.steps:
        print(f"  Step {step['step']}: {step['thought']}")
```

### One-shot: `solve()`

```python
# Auto-estimate + auto-buy the best solution in one call
receipt = mark.solve("File Ohio 2024 taxes with W2 and itemized deductions")
print(f"Tokens charged: {receipt.tokens_charged}")
```

---

## Use with Claude (Anthropic)

```python
from marktools import MarkTools
from anthropic import Anthropic

mark = MarkTools(api_key="mk_...")
client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=mark.to_anthropic(),   # ← plug in the tools
    messages=[{"role": "user", "content": "Help me file my Ohio taxes for 2024"}],
)

# Execute tool calls
for block in response.content:
    if block.type == "tool_use":
        result = mark.execute(block.name, block.input)
        print(f"Tool: {block.name} → {result[:200]}")
```

## Use with OpenAI

```python
from marktools import MarkTools
from openai import OpenAI

mark = MarkTools(api_key="mk_...")
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    tools=mark.to_openai(),      # ← plug in the tools
    messages=[{"role": "user", "content": "Help me file my Ohio taxes for 2024"}],
)

# Execute tool calls
for call in response.choices[0].message.tool_calls or []:
    import json
    result = mark.execute(call.function.name, json.loads(call.function.arguments))
```

## Use with LangChain

```python
from marktools import MarkTools

mark = MarkTools(api_key="mk_...")
tool_definitions = mark.to_langchain()
```

---

## Tools Reference

marktools exposes **3 core tools** + 1 optional:

| Tool | Cost | Description |
|------|------|-------------|
| `mark_estimate` | **Free** | Search marketplace, get pricing & ranked solutions |
| `mark_buy` | Credits | Purchase solution, get full execution plan |
| `mark_rate` | **Free** | Rate a workflow after use (improves marketplace) |
| `mark_search` | **Free** | Browse/filter marketplace workflows |

### `mark_estimate` — Search & Price

```python
estimate = mark.client.estimate(
    query="File Ohio 2024 taxes with W2 and itemized deductions",
    context={"state": "ohio", "year": 2024, "income": 87000}
)

# Returns ranked solutions:
for sol in estimate.solutions:
    print(f"  {sol.solution_id}: {sol.pricing.total_cost_tokens} tokens "
          f"({sol.pricing.savings_percentage}% savings)")
```

### `mark_buy` — Purchase Solution

```python
receipt = mark.client.buy(
    session_id=estimate.session_id,
    solution_id="sol_1"
)

# Full execution plan with steps, edge cases, domain knowledge:
for wf in receipt.execution_plan.workflows:
    for step in wf.workflow.steps:
        print(f"  {step['step']}. {step['action']}: {step['thought']}")
```

### `mark_rate` — Post-Use Feedback

```python
mark.client.rate("ohio_w2_itemized_2024", rating=5)
# or
mark.client.rate("ohio_w2_itemized_2024", vote="up")
```

---

## Privacy-First Architecture

All data is sanitized before hitting the marketplace:

```python
result = mark.client.sanitize({
    "name": "John Smith",           # ← removed
    "ssn": "123-45-6789",           # ← removed
    "exact_income": 87432.18,       # ← bucketed to "80k-100k"
    "state": "ohio",                # ← kept
    "year": 2024,                   # ← kept
})
# public_query: {"state": "ohio", "year": 2024, "exact_income": "80k-100k"}
# private_data: {"name": "John Smith", "ssn": "123-45-6789"}
```

Names, SSNs, emails, and exact incomes **never leave the agent's local environment**.

---

## Models

All responses are typed Pydantic models:

```python
from marktools import (
    Workflow,           # Marketplace workflow template
    Solution,           # Ranked solution candidate
    EstimateResult,     # Response from estimate()
    PurchaseReceipt,    # Response from buy()
    RateResult,         # Response from rate()
)
```

---

## Configuration

```python
from marktools import MarkClient

# Option 1: Pass API key directly
mark = MarkClient(api_key="mk_...")

# Option 2: Environment variable
# export MARK_API_KEY=mk_...
mark = MarkClient()

# Option 3: Custom API URL (self-hosted)
# export MARK_API_URL=http://localhost:5001
mark = MarkClient(base_url="http://localhost:5001")
```

| Env Variable | Description | Default |
|---|---|---|
| `MARK_API_KEY` | Your API key | — |
| `MARK_API_URL` | API base URL | `https://api.mark.ai` |

---

## Development

```bash
# Clone the repo
git clone https://github.com/akhaire21/treehacks-2026
cd treehacks-2026/marktools

# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/marktools

# Lint
ruff check src/
```

## License

MIT
