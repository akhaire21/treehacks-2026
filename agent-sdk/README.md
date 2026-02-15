# Agent SDK Demos

Autonomous AI agents powered by **Claude + marktools**.

These demos simulate real agents using `pip install marktools` to buy pre-solved
reasoning workflows from the Mark marketplace — autonomously.

## Setup

```bash
pip install marktools anthropic rich
export ANTHROPIC_API_KEY=sk-ant-...
export MARK_API_URL=http://localhost:5001
```

## Demos

| Script | Description | Prize Target |
|--------|-------------|--------------|
| `tax_agent.py` | Files Ohio taxes autonomously — estimates, buys, executes | Anthropic: Human Flourishing |
| `shopping_agent.py` | Smart product comparison & commerce | Visa: Future of Commerce |
| `orchestrator_agent.py` | Multi-task chaining across domains | Greylock: Best Multi-Turn Agent |
| `run_all.py` | Run all demos with rich terminal output | Demo showpiece |

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────┐
│  Claude (claude-sonnet-4-20250514)  │
│  + marktools.to_anthropic()    │
│                                │
│  Tools:                        │
│    mark_estimate  (free)       │
│    mark_buy       (credits)    │
│    mark_rate      (feedback)   │
└─────────────┬───────────┘
              │ tool_use
              ▼
┌─────────────────────────┐
│  marktools.execute()           │
│  → HTTP → Mark API             │
│  → Elasticsearch hybrid search │
│  → PII sanitization            │
│  → Token economy               │
└─────────────────────────┘
```
