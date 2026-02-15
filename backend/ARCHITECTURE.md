# Workflow Marketplace - Technical Architecture

## Table of Contents
1. [Elasticsearch Data Representation](#elasticsearch-data-representation)
2. [Time Complexity Analysis](#time-complexity-analysis)
3. [Data Models](#data-models)
4. [Search Algorithm](#search-algorithm)
5. [Tree Format Improvements](#tree-format-improvements)

---

## 1. Elasticsearch Data Representation

### Two-Index Architecture

We use a **two-index approach** instead of a single monolithic index:

```
┌─────────────────────────────────────────────────────────┐
│                    ES Serverless                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  workflows       │      │  workflows_nodes │       │
│  │  (Assets)        │      │  (Steps/Tasks)   │       │
│  ├──────────────────┤      ├──────────────────┤       │
│  │ Full workflows   │      │ Individual steps │       │
│  │ + metadata       │      │ within workflows │       │
│  │ + embeddings     │      │ + embeddings     │       │
│  └──────────────────┘      └──────────────────┘       │
│         ↓                           ↓                  │
│    Broad Search            Tree-Aware Search           │
│    (Step 1-7)              (Step 9 recursion)          │
└─────────────────────────────────────────────────────────┘
```

### Index 1: `workflows` (Assets)

**Purpose**: Store full workflow documents for broad search

**Document Structure**:
```json
{
  "_id": "ohio_w2_itemized_2024",
  "_source": {
    // Identity
    "workflow_id": "ohio_w2_itemized_2024",
    "node_type": "workflow",  // Used to filter out steps

    // Content
    "title": "Ohio 2024 IT-1040 (W2, Itemized, Married)",
    "description": "Complete Ohio state income tax filing...",
    "task_type": "tax_filing",

    // Pricing (new naming)
    "download_cost": 200,      // Charged once per unique workflow
    "execution_cost": 800,     // Charged per execution
    "token_cost": 200,         // Legacy (backward compatibility)
    "execution_tokens": 800,   // Legacy (backward compatibility)

    // Metadata for filtering
    "state": "ohio",
    "year": 2024,
    "tags": ["tax", "ohio", "w2"],
    "rating": 4.8,

    // Tree structure
    "parent_id": null,         // For hierarchical workflows
    "child_ids": [],           // Child workflow IDs
    "depth": 0,

    // Search vectors
    "embedding": [0.123, -0.456, ...],  // 1024-dim dense vector
    "full_text": "Title: Ohio 2024... | Description: Complete...",

    // Structured data (stored, not indexed)
    "steps": {...},            // Object, enabled: false
    "edge_cases": {...},       // Object, enabled: false
    "domain_knowledge": {...}  // Object, enabled: false
  }
}
```

**Key Design Decisions**:
- ✅ `embedding` field uses `dense_vector` type with `index: true` for kNN search
- ✅ `full_text` is searchable text (all content flattened)
- ✅ `steps`, `edge_cases`, `domain_knowledge` are stored as objects with `enabled: false` (not indexed, just retrieved)
- ✅ No `number_of_shards` or `number_of_replicas` (serverless handles this)

### Index 2: `workflows_nodes` (Steps/Subtasks)

**Purpose**: Enable tree-aware recursive search (Step 9 in algorithm)

**Document Structure**:
```json
{
  "_id": "ohio_w2_itemized_2024_step_3",
  "_source": {
    "node_id": "ohio_w2_itemized_2024_step_3",
    "workflow_id": "ohio_w2_itemized_2024",  // Parent workflow
    "node_type": "step",                     // "step", "subtask", "module"

    // Content
    "title": "Itemized deductions calculation for Ohio",
    "text": "Thought: Itemized deductions calculation | Action: calculate | ...",
    "capability": null,

    // Tree structure
    "parent_node_id": "ohio_w2_itemized_2024",  // Direct parent
    "ordinal": 3,                                 // Order within parent

    // Search vector
    "embedding": [0.789, -0.234, ...]  // 1024-dim dense vector
  }
}
```

**Why Separate Index?**

| Aspect | Single Index | Two Indices (Our Approach) |
|--------|--------------|----------------------------|
| **Query Type** | Must filter every query | Direct index selection |
| **Embedding Context** | Mixed contexts confuse kNN | Specific contexts per index |
| **Result Quality** | Steps pollute workflow results | Clean separation |
| **Step 9 Recursion** | Expensive filtering | Direct node search |

---

## 2. Time Complexity Analysis

### Indexing Operations

#### Loading Workflows
```python
def load_and_index_workflows(workflows_path: str):
```

**Complexity**: `O(W × (E + S))`
- `W` = number of workflows
- `E` = embedding generation time (~200ms per workflow)
- `S` = number of steps per workflow

**Breakdown**:
1. Load JSON: `O(W)` - linear parse
2. Generate workflow embeddings: `O(W × E)` - API calls to Jina
3. Extract nodes: `O(W × S)` - iterate through all steps
4. Generate node embeddings: `O(W × S × E)` - API calls
5. Bulk index workflows: `O(W)` - batch insert
6. Index nodes: `O(W × S)` - individual inserts

**Example**: 8 workflows, 67 steps
- Workflow embeddings: 8 × 200ms = 1.6s
- Node embeddings: 67 × 200ms = 13.4s
- **Total**: ~15-20 seconds

### Search Operations

#### 1. Broad Search (Step 1)
```python
def _broad_search(query: str, top_k=10) -> List[SearchResult]:
```

**Complexity**: `O(E + log(W) + k)`
- `E` = embedding generation (~200ms)
- `log(W)` = kNN HNSW traversal (logarithmic in # docs)
- `k` = number of results to return

**ES kNN Query**:
```python
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.123, ...],
    "k": 10,
    "num_candidates": 100  # 10x for better recall
  }
}
```

**HNSW Complexity**:
- Indexing: `O(log(W))` per document
- Search: `O(log(W))` - navigates hierarchical graph
- Much faster than brute force `O(W)`

#### 2. Query Decomposition (Step 4)
```python
def decompose_task(task: str) -> List[Subtask]:
```

**Complexity**: `O(C)`
- `C` = Claude API call time (~2-4 seconds)
- Returns 2-8 subtasks (bounded)

#### 3. Subtask Search (Step 5-6)
```python
def _compose_plan_from_subtasks(subtasks: List[Subtask]):
```

**Complexity**: `O(N × (E + log(W)))`
- `N` = number of subtasks (2-8)
- For each subtask: embedding + search

**Example**: 5 subtasks
- Embeddings: 5 × 200ms = 1s
- Searches: 5 × log(8) × ~50ms = ~250ms
- **Total**: ~1.3 seconds

#### 4. Recursive Split (Step 9) - Tree-Aware
```python
def _recursive_split(composite_plan, depth):
```

**Complexity**: `O(E + log(S) + log(W))`
- `E` = embedding for worst subtask
- `log(S)` = kNN search in nodes index (S = steps in workflow)
- `log(W)` = kNN search in workflows index

**Key Insight**: Searching nodes index with ~67 docs is much faster than searching workflows with all steps mixed in!

**Without Tree Format**: `O(E + log(W × S))` - search all steps in single index
**With Tree Format**: `O(E + log(S))` - search only within relevant workflow

### Overall Search Complexity

**Best Case** (direct match above threshold):
```
O(E + log(W) + C)
```
- Embedding: 200ms
- kNN search: ~50ms
- Claude scoring: 2s
- **Total**: ~2.3 seconds

**Worst Case** (recursive decomposition):
```
O(E + log(W) + C + N×(E + log(W)) + D×(E + log(S) + log(W)))
```
- `N` = subtasks (2-8)
- `D` = recursion depth (max 2)
- **Total**: ~5-7 seconds

---

## 3. Data Models

### Architecture: Dataclasses for Type Safety

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
```

**Why Dataclasses?**
- ✅ Type hints for IDE autocomplete
- ✅ Automatic `__init__`, `__repr__`
- ✅ Immutable by default (safer)
- ✅ Easy serialization with `to_dict()` / `from_dict()`

### Core Models

#### 1. `Subtask` - Query Decomposition Result
```python
@dataclass
class Subtask:
    text: str           # "File Ohio state taxes"
    task_type: str      # "tax_filing" (for filtering)
    weight: float       # 1.0 (importance)
    rationale: str      # Why this subtask exists
```

**Purpose**: Represents one piece of a decomposed complex query

**Example**:
```python
subtask = Subtask(
    text="Calculate Ohio AGI with pension adjustments",
    task_type="tax_filing",
    weight=0.9,
    rationale="Ohio has specific AGI calculation rules"
)
```

#### 2. `Workflow` - Reusable Template
```python
@dataclass
class Workflow:
    # Identity
    workflow_id: str
    title: str
    description: str
    task_type: str

    # Pricing (NEW naming - clear semantics)
    download_cost: int      # Charged ONCE per unique workflow_id
    execution_cost: int     # Charged PER execution/node

    # Metadata
    node_type: str = "workflow"
    state: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    rating: float = 0.0

    # Search
    embedding: Optional[List[float]] = None
    similarity_score: float = 0.0

    # Tree structure
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    depth: int = 0

    # Content
    steps: List[Dict[str, Any]] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)

    @property
    def total_cost(self) -> int:
        """Total cost = download + execution"""
        return self.download_cost + self.execution_cost
```

**Key Property**: `total_cost`
- ✅ Computed property (not stored)
- ✅ Always consistent
- ✅ Used in API responses and logging

**Backward Compatibility**:
```python
@classmethod
def from_dict(cls, d: Dict[str, Any]) -> "Workflow":
    # Handle BOTH old and new field names
    download_cost = d.get("download_cost") or d.get("token_cost", 0)
    execution_cost = d.get("execution_cost") or d.get("execution_tokens", 0)
    # ...
```

#### 3. `WorkflowNodeDoc` - Searchable Step/Subtask
```python
@dataclass
class WorkflowNodeDoc:
    node_id: str                    # "ohio_w2_itemized_2024_step_3"
    workflow_id: str                # Parent workflow
    node_type: str                  # "step" | "subtask" | "module"

    title: str                      # "Calculate Ohio AGI"
    text: str                       # Full step description
    capability: Optional[str]       # What this step does

    parent_node_id: Optional[str]   # Direct parent
    ordinal: int                    # Order within parent

    embedding: Optional[List[float]]  # Dense vector
    score: float = 0.0
```

**Purpose**: Enables Step 9 tree-aware recursion

**Created From Workflows**:
```python
def extract_nodes_from_workflow(workflow: Workflow) -> List[WorkflowNodeDoc]:
    nodes = []
    for i, step in enumerate(workflow.steps):
        node = WorkflowNodeDoc(
            node_id=f"{workflow.workflow_id}_step_{step['step']}",
            workflow_id=workflow.workflow_id,
            node_type="step",
            title=step.get("thought", f"Step {i}"),
            text=f"Thought: {step['thought']} | Action: {step['action']}",
            parent_node_id=workflow.workflow_id,
            ordinal=step.get("step", i)
        )
        nodes.append(node)
    return nodes
```

#### 4. `SubtaskNode` - Node in Execution DAG
```python
@dataclass
class SubtaskNode:
    id: str
    description: str
    workflow: Workflow              # Full workflow object
    dependencies: List[str]         # Parent node IDs
    children: List[str]             # Child node IDs
    weight: float = 1.0
    confidence_score: float = 0.0

    @property
    def download_cost(self) -> int:
        return self.workflow.download_cost

    @property
    def execution_cost(self) -> int:
        return self.workflow.execution_cost

    @property
    def total_cost(self) -> int:
        # Naive sum - DAG level deduplicates download costs
        return self.download_cost + self.execution_cost
```

#### 5. `ExecutionDAG` - Complete Solution
```python
@dataclass
class ExecutionDAG:
    nodes: Dict[str, SubtaskNode]
    root_ids: List[str]
    execution_order: List[str]

    # Pricing (PROPERLY deduplicated)
    total_download_cost: int    # Sum of UNIQUE workflow costs
    total_execution_cost: int   # Sum of ALL node execution costs

    coverage: str               # "5/5 subtasks matched"
    overall_confidence: float

    @property
    def total_cost(self) -> int:
        return self.total_download_cost + self.total_execution_cost
```

**Critical Pricing Logic**:
```python
def to_dict_with_workflows(self) -> Dict[str, Any]:
    unique_workflow_ids = set()
    recalc_download_cost = 0
    recalc_execution_cost = 0

    for node in self.nodes.values():
        # Download cost: charge ONCE per unique workflow
        if node.workflow_id not in unique_workflow_ids:
            unique_workflow_ids.add(node.workflow_id)
            recalc_download_cost += node.download_cost

        # Execution cost: charge PER node
        recalc_execution_cost += node.execution_cost

    return {
        "pricing": {
            "total_download_cost": recalc_download_cost,
            "total_execution_cost": recalc_execution_cost,
            "total_cost_tokens": recalc_download_cost + recalc_execution_cost
        }
    }
```

**Example**: 3 nodes all use the same workflow
- Download cost: 200 tokens (charged ONCE)
- Execution cost: 800 × 3 = 2400 tokens (charged per node)
- **Total**: 2600 tokens (not 3000!)

#### 6. `SearchPlan` - Final Result
```python
@dataclass
class SearchPlan:
    plan_type: str  # "direct" or "composite"
    workflows: List[Workflow]
    overall_score: float

    # For composite plans
    subtasks: List[Subtask] = field(default_factory=list)
    subtask_workflow_mapping: Dict[int, int] = field(default_factory=dict)
    coverage: str = ""

    @property
    def is_composite(self) -> bool:
        return self.plan_type == "composite"
```

---

## 4. Search Algorithm

### Overview: Recursive Query Decomposition with Scoring

```
┌─────────────────────────────────────────────────────┐
│              User Query                              │
│      "I need to file Ohio 2024 taxes"              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Step 1: Broad Search│
         │  (kNN + Hybrid)      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Step 2: Score Best  │
         │  (Claude evaluates)  │
         └──────────┬───────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    Score ≥ τ_good?        Score < τ_good?
         │                     │
         ▼                     ▼
    ┌─────────┐      ┌──────────────────────┐
    │ Return  │      │  Step 3: Decompose   │
    │ Direct  │      │  (Claude → Subtasks) │
    └─────────┘      └──────────┬───────────┘
                                │
                                ▼
                     ┌────────────────────────┐
                     │  Step 4-6: Search Each │
                     │  Subtask + Compose     │
                     └──────────┬─────────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
              Improvement ≥ ε?      Still weak?
                     │                     │
                     ▼                     ▼
              ┌──────────┐     ┌────────────────────┐
              │ Return   │     │  Step 9: Recursive │
              │Composite │     │  Split (Tree-Aware)│
              └──────────┘     └──────────┬─────────┘
                                          │
                                          ▼
                               ┌───────────────────┐
                               │ Search Nodes Index│
                               │ Refine Query      │
                               └───────────────────┘
```

### Parameters (Tunable in `.env`)

```python
τ_good = 0.85  # SCORE_THRESHOLD_GOOD
ε = 0.1        # SCORE_IMPROVEMENT_EPSILON
max_depth = 2  # MAX_RECURSION_DEPTH
```

### Detailed Steps

#### Step 1: Broad Search
```python
def _broad_search(query: str, top_k=10) -> List[SearchResult]:
    # Generate query embedding
    query_embedding = self.embedding_service.embed(
        query,
        task="retrieval.query"  # IMPORTANT: query mode
    )

    # Hybrid search: kNN + text
    results = self.es_service.hybrid_search(
        query_embedding=query_embedding,
        query_text=query,
        top_k=top_k
    )

    # Filter to workflows only (not steps)
    workflow_results = [
        r for r in results
        if r["_source"]["node_type"] == "workflow"
    ]

    return [Workflow.from_es_hit(hit) for hit in workflow_results]
```

**Hybrid Search Formula**:
```python
score = 0.7 × cosine_similarity(query_vec, doc_vec) +
        0.3 × bm25_score(query_text, doc_text)
```

#### Step 2: Score Plan Quality
```python
def score_plan_quality(task: str, workflow: Workflow) -> float:
    """Claude evaluates how well workflow matches task"""

    prompt = f"""
Task: "{task}"

Workflow:
Title: {workflow.title}
Description: {workflow.description}
Task Type: {workflow.task_type}

Rate 0.0-1.0 how well this workflow solves the task.
Output JSON: {{"score": 0.85, "reasoning": "..."}}
"""

    response = claude.generate(prompt)
    return parse_json(response)["score"]
```

**Why Claude Scoring?**
- ✅ Semantic understanding beyond embeddings
- ✅ Considers edge cases and requirements
- ✅ Domain-aware (knows tax != travel)

#### Step 3: Decompose Task
```python
def decompose_task(task: str) -> List[Subtask]:
    """Break complex task into 2-8 subtasks"""

    prompt = f"""
Decompose this task into 2-8 independent subtasks:
"{task}"

Output JSON array:
[
  {{
    "text": "subtask description",
    "task_type": "category",
    "weight": 1.0,
    "rationale": "why needed"
  }},
  ...
]
"""

    response = claude.generate(prompt)
    return [Subtask.from_dict(st) for st in parse_json(response)]
```

**Example**:
```
Task: "File Ohio 2024 taxes with W2 income"

Subtasks:
1. "gather and organize W2 forms" (weight: 0.8)
2. "process W2 income for tax filing" (weight: 1.0)
3. "calculate Ohio state tax deductions" (weight: 0.8)
4. "complete Ohio IT-1040 form" (weight: 0.9)
5. "submit return electronically" (weight: 0.7)
```

#### Step 4-6: Compose Plan from Subtasks
```python
def _compose_plan_from_subtasks(subtasks: List[Subtask]) -> CompositePlan:
    best_workflows = []
    matched_subtasks = []

    # Search each subtask
    for subtask in subtasks:
        results = self._broad_search(subtask.text, top_k=3)
        if results:
            best = results[0]  # Pick best match
            best_workflows.append(best)
            matched_subtasks.append(subtask)

    # Score composite plan
    weighted_scores = []
    for subtask, workflow in zip(matched_subtasks, best_workflows):
        score = claude.score_plan_quality(subtask.text, workflow)
        weighted_scores.append(score * subtask.weight)

    # CRITICAL: Factor in coverage
    avg_quality = sum(weighted_scores) / sum(st.weight for st in matched_subtasks)
    coverage_ratio = len(matched_subtasks) / len(subtasks)
    overall_score = coverage_ratio * avg_quality

    return CompositePlan(
        workflows=best_workflows,
        subtasks=matched_subtasks,
        overall_score=overall_score,
        coverage=f"{len(matched_subtasks)}/{len(subtasks)}"
    )
```

**Key Insight**: Coverage ratio prevents accepting "1/6 subtasks perfectly matched" as good!

#### Step 9: Recursive Split (Tree-Aware)
```python
def _recursive_split(composite_plan, depth) -> Optional[CompositePlan]:
    # Find worst-matching subtask
    worst_idx = min(
        range(len(composite_plan.subtasks)),
        key=lambda i: claude.score_plan_quality(
            composite_plan.subtasks[i].text,
            composite_plan.workflows[i]
        )
    )

    worst_subtask = composite_plan.subtasks[worst_idx]
    worst_workflow = composite_plan.workflows[worst_idx]

    # TREE-AWARE: Search within workflow's indexed nodes
    node_hits = self.es_service.search_nodes(
        workflow_id=worst_workflow.workflow_id,
        query_text=worst_subtask.text,
        query_embedding=embed(worst_subtask.text, task="retrieval.query"),
        node_type="step",
        top_k=3
    )

    if node_hits:
        best_node = WorkflowNodeDoc.from_es_hit(node_hits[0])

        # Use node to refine query
        refined_query = f"{worst_subtask.text}\nSpecifically: {best_node.text}"

        # Search for better workflow
        refined_results = self._broad_search(refined_query, top_k=3)

        if refined_results:
            better_workflow = refined_results[0]
            new_score = claude.score_plan_quality(worst_subtask.text, better_workflow)

            if new_score > old_score:
                # Replace with better workflow
                improved_workflows = composite_plan.workflows.copy()
                improved_workflows[worst_idx] = better_workflow
                return recompute_plan(improved_workflows, composite_plan.subtasks)

    # Fallback: LLM-based recursive decomposition
    return self.search(worst_subtask.text, depth=depth+1)
```

---

## 5. Tree Format Improvements

### Problem: Single-Index Approach (Before)

```
workflows (single index)
├── ohio_w2_itemized_2024 (workflow)
│   ├── step_1 (embedded separately)
│   ├── step_2 (embedded separately)
│   ├── step_3 (embedded separately)
│   └── ...
├── california_540_2024 (workflow)
│   ├── step_1
│   ├── step_2
│   └── ...
└── tokyo_family_trip (workflow)
    ├── step_1
    └── ...
```

**Issues**:
1. ❌ Steps pollute workflow search results
2. ❌ Need to filter `node_type="workflow"` on EVERY query
3. ❌ kNN search mixes workflows and steps (different contexts)
4. ❌ Hard to search "within a specific workflow"
5. ❌ No clean separation of concerns

### Solution: Two-Index Approach (After)

```
workflows (assets index)          workflows_nodes (nodes index)
├── ohio_w2_itemized_2024        ├── ohio_w2_itemized_2024_step_1
├── california_540_2024          ├── ohio_w2_itemized_2024_step_2
└── tokyo_family_trip            ├── ohio_w2_itemized_2024_step_3
                                 ├── california_540_2024_step_1
                                 ├── california_540_2024_step_2
                                 └── ...
```

**Benefits**:

#### 1. **Clean Broad Search** (Steps 1-7)
```python
# OLD: Must filter every query
results = es.search(
    index="workflows",
    query={
        "bool": {
            "must": [{"match": {"description": query}}],
            "filter": [{"term": {"node_type": "workflow"}}]  # Extra filter!
        }
    }
)

# NEW: Direct index selection
results = es.search(
    index="workflows",  # Only workflows, no filtering needed
    query={"match": {"description": query}}
)
```

**Performance**: Eliminates filter overhead on every query

#### 2. **Tree-Aware Step 9** - Key Innovation!

**OLD Approach**: Search all steps in monolithic index
```python
# Search steps within workflow (SLOW - searches ALL steps)
results = es.search(
    index="workflows",
    query={
        "bool": {
            "filter": [
                {"term": {"parent_id": workflow_id}},  # Filter to workflow
                {"term": {"node_type": "step"}}         # Filter to steps
            ],
            "must": [{"knn": {"field": "embedding", ...}}]
        }
    }
)
```

**Time Complexity**: `O(log(W × S))` where W=workflows, S=steps per workflow
- For 8 workflows × 10 steps = 80 docs to search through

**NEW Approach**: Direct node index search
```python
# Search dedicated nodes index
results = es.search(
    index="workflows_nodes",
    query={
        "bool": {
            "filter": [{"term": {"workflow_id": workflow_id}}],
            "must": [{"knn": {"field": "embedding", ...}}]
        }
    }
)
```

**Time Complexity**: `O(log(S))` where S=steps in THIS workflow
- For 1 workflow × 10 steps = 10 docs to search through

**Speedup**: ~8x faster for this example!

#### 3. **Better Embedding Context**

**OLD**: Mixed contexts confuse kNN
```
Embedding space (mixed):
  [Workflow: "Ohio 2024 taxes"]  ←──┐
  [Step: "Calculate AGI"]            │ These are VERY
  [Workflow: "Tokyo trip"]           │ different contexts!
  [Step: "Visit Senso-ji temple"]  ←─┘
  [Step: "File federal return"]
```

Embeddings for workflows and steps have different semantic meanings!
- Workflow embedding: "What does this solve?"
- Step embedding: "How do I do this specific action?"

**NEW**: Separate contexts
```
workflows index:                workflows_nodes index:
  [Ohio 2024 taxes]               [Calculate AGI]
  [Tokyo trip]                    [Visit Senso-ji]
  [California taxes]              [File federal return]

  ↑ All "solution" context        ↑ All "action" context
```

kNN works better when all vectors are in the same semantic space!

#### 4. **Recursive Refinement**

**Step 9 Flow with Tree Format**:

```
Query: "File Ohio taxes"
  ↓
[Broad Search] → Find "Ohio 2024 IT-1040"
  ↓
[Score] → 0.70 (below threshold)
  ↓
[Decompose] →
  Subtask 1: "Calculate Ohio AGI"
  Subtask 2: "Complete IT-1040"
  ↓
[Compose] → Both match same workflow (score: 0.75)
  ↓
[Recursive Split] → Search NODES index for "Calculate Ohio AGI"
  ↓
[Find Node] → "Step 2: Calculate Ohio AGI with pension adjustments"
  ↓
[Refined Query] → "Calculate Ohio AGI with pension adjustments"
  ↓
[Better Match] → More specific workflow or better section
```

**Why This Works**:
1. Node provides **specific context** from within workflow
2. Refined query has **more detail** than original
3. Search is **fast** (only ~10 nodes per workflow)
4. Can find **better matches** that weren't obvious from high-level description

#### 5. **Scalability**

| Metric | Single Index | Two Indices |
|--------|--------------|-------------|
| **Total Docs** | 8 workflows + 67 steps = 75 | 8 + 67 = 75 (same) |
| **Workflow Search** | Search 75, filter to 8 | Search 8 directly |
| **Node Search** | Search 75, filter to ~10 | Search ~10 directly |
| **kNN Index Size** | 75 docs, mixed context | 8 + 67, separate contexts |
| **Query Filters** | 2 filters per query | 0-1 filters per query |

**At Scale** (1000 workflows, 10k steps):

| Operation | Single Index | Two Indices | Improvement |
|-----------|--------------|-------------|-------------|
| Workflow Search | log(11000) ≈ 13.4 | log(1000) ≈ 10.0 | **25% faster** |
| Node Search | log(11000) ≈ 13.4 | log(10) ≈ 3.3 | **75% faster** |

---

## Summary

### Key Architectural Decisions

1. **Two-Index Approach**
   - ✅ Clean separation: workflows vs nodes
   - ✅ Better embedding contexts
   - ✅ Faster tree-aware search (Step 9)

2. **Dataclass Models**
   - ✅ Type safety and IDE support
   - ✅ Clear pricing semantics
   - ✅ Easy serialization

3. **Hybrid Search**
   - ✅ kNN for semantic similarity
   - ✅ BM25 for keyword matching
   - ✅ Weighted combination (70/30)

4. **Claude-Based Scoring**
   - ✅ Semantic understanding
   - ✅ Domain awareness
   - ✅ Better than embeddings alone

5. **Tree-Aware Recursion**
   - ✅ Leverages hierarchical structure
   - ✅ Fast node-level search
   - ✅ Refinement with context

### Time Complexity Wins

- **Indexing**: `O(W × S × E)` - unavoidable (need all embeddings)
- **Broad Search**: `O(log(W))` - fast with HNSW
- **Node Search**: `O(log(S))` - **8x faster** with separate index
- **Overall Search**: ~2-7 seconds end-to-end

### Trade-offs

**Pros**:
- ✅ Fast and accurate search
- ✅ Scalable to 1000s of workflows
- ✅ Clean architecture
- ✅ Tree-aware refinement

**Cons**:
- ⚠️ Two indices to maintain
- ⚠️ More complex indexing logic
- ⚠️ Claude API costs for scoring

**Verdict**: The two-index approach is **clearly superior** for tree-structured workflow data! 🎯

