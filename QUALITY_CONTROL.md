# Quality Control: `require_close_match` Feature

## Overview

The `require_close_match` parameter provides quality control for the marketplace by preventing the system from returning poor-quality workflow matches. When enabled, the system will return **nothing** if no close matches are found after exhausting the maximum recursion depth.

## Motivation

### The Problem

Without quality control, the system might return workflows that are tangentially related but not truly helpful:

```
Query: "File taxes for Mars colony mining in 2099"

Without quality control:
✓ Returns: Generic tax filing workflow (score: 0.35)
❌ Problem: Workflow is for Earth taxes in 2024
❌ Result: Agent pays for irrelevant workflow
```

### The Solution

With `require_close_match=True`:

```
Query: "File taxes for Mars colony mining in 2099"

With quality control:
✓ Tries recursive decomposition up to max_depth
✓ Best score after depth 2: 0.35 (below threshold of 0.6)
✓ Returns: Empty results with quality_control metadata
✓ Result: Agent not charged, can build solution from scratch
```

---

## How It Works

### Algorithm Flow

```
1. Search for workflows (broad search)
   └─ Score best match

2. If score >= SCORE_THRESHOLD_GOOD (0.85):
   └─ ✓ Return immediately (good match found)

3. If score < threshold:
   └─ Decompose into subtasks
   └─ Search each subtask recursively (up to MAX_RECURSION_DEPTH)
   └─ Compose best solution

4. After exhausting max_depth:
   └─ Check: best_score >= MIN_ACCEPTABLE_SCORE?

5a. If require_close_match=False (default):
    └─ Return best effort results (even if score is low)

5b. If require_close_match=True:
    └─ If best_score >= MIN_ACCEPTABLE_SCORE:
        └─ ✓ Return solutions
    └─ Else (score too low):
        └─ ✓ Return empty results with quality_control metadata
```

---

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Quality Control Parameters
MIN_ACCEPTABLE_SCORE=0.6         # Minimum score to return results
MAX_RECURSION_DEPTH=2            # Max search depth before giving up
SCORE_THRESHOLD_GOOD=0.85        # Score for early exit (good match)
```

### Score Thresholds

| Threshold | Value | Meaning |
|-----------|-------|---------|
| `SCORE_THRESHOLD_GOOD` | 0.85 | Excellent match - return immediately |
| `MIN_ACCEPTABLE_SCORE` | 0.6 | Minimum acceptable - don't return below this if require_close_match=True |

**Score Interpretation:**
- `0.85+` - Excellent match (direct, no decomposition needed)
- `0.6-0.85` - Good match (acceptable after decomposition)
- `< 0.6` - Poor match (only return if require_close_match=False)

---

## API Usage

### Request Format

```json
POST /api/estimate

{
  "query": "Natural language query",
  "context": {
    "state": "ohio",
    "year": 2024
  },
  "top_k": 5,
  "require_close_match": true  // ← NEW PARAMETER
}
```

### Response (Quality Control Triggered)

When no close matches are found:

```json
{
  "query": {
    "sanitized": {
      "query": "File taxes for [LOCATION] [YEAR]"
    },
    "privacy_protected": true
  },
  "decomposition": {
    "num_subtasks": 3,
    "subtasks": [
      {
        "text": "Calculate Mars colony tax rates",
        "task_type": "calculation",
        "weight": 0.33
      },
      {
        "text": "Apply interplanetary deductions",
        "task_type": "tax_filing",
        "weight": 0.33
      },
      {
        "text": "File with Mars IRS",
        "task_type": "filing",
        "weight": 0.34
      }
    ]
  },
  "solutions": [],           // ← EMPTY
  "num_solutions": 0,        // ← ZERO
  "session_id": null,        // ← NO SESSION
  "quality_control": {       // ← METADATA
    "triggered": true,
    "reason": "No close matches found after exhausting max recursion depth",
    "max_depth_reached": true,
    "final_depth": 2,
    "best_score": 0.35,
    "min_required_score": 0.6
  }
}
```

### Response (Good Matches Found)

When matches meet the threshold:

```json
{
  "query": {...},
  "decomposition": {...},
  "solutions": [
    {
      "solution_id": "sol_1",
      "rank": 1,
      "confidence_score": 0.88,
      "pricing": {...},
      "structure": {...},
      "workflows_summary": [...]
    }
  ],
  "num_solutions": 3,
  "session_id": "session_abc123"
  // No quality_control field = quality check passed
}
```

---

## Use Cases

### When to Use `require_close_match=False` (Default)

✓ **Exploratory searches** - User browsing marketplace
✓ **Brainstorming** - Looking for inspiration
✓ **Flexible requirements** - Willing to adapt workflows
✓ **Research mode** - Understanding what's available

**Example:**
```python
response = estimate_price_and_search(
    raw_query="Help me plan a trip",
    require_close_match=False  # Show me what you have
)
# Returns: Various trip planning workflows (even if not perfect match)
```

### When to Use `require_close_match=True`

✓ **Production agents** - Automated task execution
✓ **Cost-conscious** - Only pay for quality matches
✓ **Specific requirements** - Need exact workflow
✓ **Quality over quantity** - Prefer nothing over bad results

**Example:**
```python
response = estimate_price_and_search(
    raw_query="File Ohio 2024 taxes with W2 and itemized deductions",
    require_close_match=True  # Only return if you have what I need
)
# Returns: Only high-quality, relevant workflows (or nothing)
```

---

## Examples

### Example 1: Good Match

```python
# Query that has good workflows in marketplace
query = "I need to file my California 2024 taxes with W2 income"

# Without quality control
response1 = orchestrator.estimate_price_and_search(
    raw_query=query,
    require_close_match=False
)
# ✓ Returns: 3 solutions, score: 0.92

# With quality control
response2 = orchestrator.estimate_price_and_search(
    raw_query=query,
    require_close_match=True
)
# ✓ Returns: 3 solutions, score: 0.92 (same result)
```

### Example 2: Poor Match

```python
# Query with no good workflows
query = "File taxes for Mars colony mining operation in 2099"

# Without quality control
response1 = orchestrator.estimate_price_and_search(
    raw_query=query,
    require_close_match=False
)
# ⚠️ Returns: 1 solution (generic tax workflow), score: 0.35
# Problem: Poor quality, not helpful

# With quality control
response2 = orchestrator.estimate_price_and_search(
    raw_query=query,
    require_close_match=True
)
# ✓ Returns: Empty results with quality_control metadata
# ✓ Agent knows: "No matches, build from scratch"
```

### Example 3: Partial Match

```python
# Query with some matching workflows
query = "File CA taxes with crypto gains and rental income from lunar properties"

response = orchestrator.estimate_price_and_search(
    raw_query=query,
    require_close_match=True
)

if response['num_solutions'] > 0:
    # ✓ Found workflows for: CA taxes, crypto, rental
    # ✓ Coverage: 3/4 subtasks (75%)
    # ✓ Score: 0.68 (above 0.6 threshold)
    print("Using marketplace workflows for most subtasks")
    print("Build custom solution for 'lunar properties'")
else:
    # Coverage too low or score below threshold
    print("Build entire solution from scratch")
```

---

## Implementation Details

### Files Modified

1. **[config.py](backend/config.py#L56)** - Added `MIN_ACCEPTABLE_SCORE` parameter
2. **[models.py](backend/models.py#L518-L519)** - Added `max_depth_reached` and `final_depth` to `SearchPlan`
3. **[query_decomposer.py](backend/query_decomposer.py#L245-L261)** - Track depth and flag when max reached
4. **[orchestrator.py](backend/orchestrator.py#L165-L197)** - Quality control check and empty response
5. **[api.py](backend/api.py#L154-L161)** - Accept `require_close_match` parameter

### Testing

Run the test suite:

```bash
cd backend
python test_quality_control.py
```

This will test:
- ✓ Realistic queries (should find matches)
- ✓ Unrealistic queries (should trigger quality control)
- ✓ Edge cases (partial matches)

---

## Benefits

### For Agents

✓ **Cost savings** - Don't pay for irrelevant workflows
✓ **Clear signals** - Know when marketplace can't help
✓ **Better decisions** - Can fall back to from-scratch implementation
✓ **Quality guarantee** - Only get workflows above threshold

### For Marketplace

✓ **Reputation** - Don't sell poor quality matches
✓ **Trust** - Agents know they'll get value for tokens
✓ **Analytics** - Track queries that trigger quality control
✓ **Gap analysis** - Identify missing workflows to build

---

## Monitoring & Analytics

### Log Quality Control Events

```python
if 'quality_control' in response and response['quality_control']['triggered']:
    analytics.log({
        'event': 'quality_control_triggered',
        'query': sanitized_query,
        'decomposition': response['decomposition']['subtasks'],
        'best_score': response['quality_control']['best_score'],
        'final_depth': response['quality_control']['final_depth']
    })
    # Later: Analyze patterns to build new workflows
```

### Metrics to Track

- **Trigger rate** - % of queries that trigger quality control
- **Score distribution** - How close queries get to threshold
- **Common patterns** - What types of queries have no matches
- **Depth usage** - How often max depth is reached

---

## Future Enhancements

### 1. Adaptive Thresholds

```python
# Adjust threshold based on query complexity
if len(subtasks) > 5:
    threshold = 0.5  # More lenient for complex queries
else:
    threshold = 0.6  # Stricter for simple queries
```

### 2. Partial Purchase Option

```python
# Allow buying subset of workflows that match well
if coverage >= 0.75 and best_score >= 0.6:
    return {
        "partial_match": True,
        "matched_subtasks": [0, 1, 2],  # 3 out of 4
        "unmatched_subtasks": [3],      # Build this from scratch
        "solutions": [...]
    }
```

### 3. Suggestion Engine

```python
if quality_control_triggered:
    suggestions = find_similar_queries()
    return {
        "solutions": [],
        "quality_control": {...},
        "suggestions": [
            "Did you mean: File Ohio 2024 taxes?",
            "Try: General tax filing workflow",
            "Similar: California tax filing"
        ]
    }
```

---

## Summary

The `require_close_match` parameter provides **quality control** for the marketplace:

| Parameter | Behavior |
|-----------|----------|
| `require_close_match=False` (default) | Return best effort, even if score is low |
| `require_close_match=True` | Only return if score >= MIN_ACCEPTABLE_SCORE after max_depth |

**Configuration:**
- `MIN_ACCEPTABLE_SCORE=0.6` (configurable)
- `MAX_RECURSION_DEPTH=2` (max search depth)
- `SCORE_THRESHOLD_GOOD=0.85` (early exit threshold)

**Quality control triggers when:**
1. Max recursion depth is reached **AND**
2. Best score < MIN_ACCEPTABLE_SCORE **AND**
3. `require_close_match=True`

**Result:** Empty solutions list with quality control metadata explaining why.
