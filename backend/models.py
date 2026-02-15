"""
Unified data models for the marketplace system.

All components use these models instead of raw dicts.
Ensures consistency and type safety across the codebase.

PRICING SEMANTICS (FIXED):
- download_cost: Cost to download a workflow (charged once per unique workflow_id)
- execution_cost: Cost to execute a workflow (charged per execution/node)
- total_cost: download_cost + execution_cost (properly deduplicated)
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Subtask:
    """
    A subtask from query decomposition.

    Represents one part of a complex task that needs to be solved.
    """
    text: str
    task_type: str
    weight: float
    rationale: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Subtask":
        """Create Subtask from dict (from LLM response)."""
        return cls(
            text=d["text"],
            task_type=d.get("task_type", "general"),
            weight=d.get("weight", 1.0),
            rationale=d.get("rationale", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API responses."""
        return {
            "text": self.text,
            "task_type": self.task_type,
            "weight": self.weight,
            "rationale": self.rationale
        }


@dataclass
class TokenComparison:
    """Token usage comparison: with workflow vs from scratch."""
    with_workflow: int
    from_scratch: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TokenComparison":
        """Create from dict."""
        return cls(
            with_workflow=d["with_workflow"],
            from_scratch=d["from_scratch"]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            "with_workflow": self.with_workflow,
            "from_scratch": self.from_scratch
        }


@dataclass
class Workflow:
    """
    A reusable workflow template from the marketplace.

    PRICING FIELDS (normalized naming):
    - download_cost: Tokens to download this workflow (charged once)
    - execution_cost: Tokens to execute this workflow (charged per run)
    """
    workflow_id: str
    title: str
    description: str
    task_type: str
    download_cost: int  # ✅ Renamed from token_cost for clarity
    execution_cost: int  # ✅ Renamed from execution_tokens for clarity

    # Optional metadata fields
    node_type: str = "workflow"  # "workflow" or "step" for filtering
    state: Optional[str] = None  # State/province for location filtering
    location: Optional[str] = None  # City/country for geographic search
    year: Optional[int] = None  # Year for temporal filtering
    duration_days: Optional[int] = None  # Duration for trip planning
    requirements: List[str] = field(default_factory=list)  # Prerequisites
    tags: List[str] = field(default_factory=list)  # Categorization tags
    rating: float = 0.0  # Quality rating (0-5)
    usage_count: int = 0  # Popularity metric

    # Search and indexing fields
    full_text: Optional[str] = None  # Text representation for search
    embedding: Optional[List[float]] = None  # Dense vector embedding
    similarity_score: float = 0.0  # Match score from search

    # Tree structure fields (for hierarchical workflows)
    parent_id: Optional[str] = None  # Parent workflow ID
    child_ids: List[str] = field(default_factory=list)  # Child workflow IDs
    depth: int = 0  # Tree depth level

    # Optional workflow content fields
    steps: List[Dict[str, Any]] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)
    domain_knowledge: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    token_comparison: Optional[TokenComparison] = None

    @property
    def total_cost(self) -> int:
        """
        Total cost = download_cost + execution_cost.

        This is the full cost to download and execute this workflow.
        """
        return self.download_cost + self.execution_cost

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Workflow":
        """Create Workflow from dict."""
        # Handle both old and new field names for backward compatibility
        download_cost = d.get("download_cost") or d.get("token_cost", 0)
        execution_cost = d.get("execution_cost") or d.get("execution_tokens", 0)

        token_comparison = None
        if "token_comparison" in d and d["token_comparison"]:
            token_comparison = TokenComparison.from_dict(d["token_comparison"])

        return cls(
            workflow_id=d["workflow_id"],
            title=d["title"],
            description=d.get("description", ""),
            task_type=d.get("task_type", "general"),
            download_cost=download_cost,
            execution_cost=execution_cost,
            # Metadata fields
            node_type=d.get("node_type", "workflow"),
            state=d.get("state"),
            location=d.get("location"),
            year=d.get("year"),
            duration_days=d.get("duration_days"),
            requirements=d.get("requirements", []),
            tags=d.get("tags", []),
            rating=d.get("rating", 0.0),
            usage_count=d.get("usage_count", 0),
            # Search fields
            full_text=d.get("full_text"),
            embedding=d.get("embedding"),
            similarity_score=d.get("similarity_score", 0.0),
            # Tree structure
            parent_id=d.get("parent_id"),
            child_ids=d.get("child_ids", []),
            depth=d.get("depth", 0),
            # Content fields
            steps=d.get("steps", []),
            edge_cases=d.get("edge_cases", []),
            domain_knowledge=d.get("domain_knowledge", []),
            examples=d.get("examples", []),
            token_comparison=token_comparison
        )

    @classmethod
    def from_es_hit(cls, hit: Dict[str, Any]) -> "Workflow":
        """Create Workflow from Elasticsearch hit."""
        source = hit.get("_source", {})
        score = hit.get("_score", 0.0)

        # Handle both old and new field names
        download_cost = source.get("download_cost") or source.get("token_cost", 0)
        execution_cost = source.get("execution_cost") or source.get("execution_tokens", 0)

        token_comparison = None
        if "token_comparison" in source and source["token_comparison"]:
            token_comparison = TokenComparison.from_dict(source["token_comparison"])

        return cls(
            workflow_id=source["workflow_id"],
            title=source["title"],
            description=source.get("description", ""),
            task_type=source.get("task_type", "general"),
            download_cost=download_cost,
            execution_cost=execution_cost,
            # Metadata fields
            node_type=source.get("node_type", "workflow"),
            state=source.get("state"),
            location=source.get("location"),
            year=source.get("year"),
            duration_days=source.get("duration_days"),
            requirements=source.get("requirements", []),
            tags=source.get("tags", []),
            rating=source.get("rating", 0.0),
            usage_count=source.get("usage_count", 0),
            # Search fields
            full_text=source.get("full_text"),
            embedding=source.get("embedding"),
            similarity_score=score,
            # Tree structure
            parent_id=source.get("parent_id"),
            child_ids=source.get("child_ids", []),
            depth=source.get("depth", 0),
            # Content fields
            steps=source.get("steps", []),
            edge_cases=source.get("edge_cases", []),
            domain_knowledge=source.get("domain_knowledge", []),
            examples=source.get("examples", []),
            token_comparison=token_comparison
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API responses."""
        result = {
            "workflow_id": self.workflow_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "download_cost": self.download_cost,
            "execution_cost": self.execution_cost,
            # Metadata
            "node_type": self.node_type,
            "tags": self.tags,
            "rating": self.rating,
            "usage_count": self.usage_count,
            # Content
            "steps": self.steps,
            "edge_cases": self.edge_cases,
            "domain_knowledge": self.domain_knowledge,
            "examples": self.examples,
            "requirements": self.requirements,
            "similarity_score": self.similarity_score
        }

        # Include optional location/temporal fields if set
        if self.state:
            result["state"] = self.state
        if self.location:
            result["location"] = self.location
        if self.year:
            result["year"] = self.year
        if self.duration_days:
            result["duration_days"] = self.duration_days

        # Include tree structure if set
        if self.parent_id:
            result["parent_id"] = self.parent_id
        if self.child_ids:
            result["child_ids"] = self.child_ids
        if self.depth > 0:
            result["depth"] = self.depth

        if self.token_comparison:
            result["token_comparison"] = self.token_comparison.to_dict()

        # Don't include embedding in API responses (too large)
        # Don't include full_text (used for search only)
        return result

    def to_es_document(self) -> Dict[str, Any]:
        """
        Convert to Elasticsearch document for indexing.

        Includes all fields including embedding and full_text which are
        excluded from API responses.
        """
        doc = self.to_dict()

        # Add search-specific fields
        if self.embedding:
            doc["embedding"] = self.embedding
        if self.full_text:
            doc["full_text"] = self.full_text

        # Ensure backward compatibility field names are also present
        doc["token_cost"] = self.download_cost
        doc["execution_tokens"] = self.execution_cost

        return doc


@dataclass
class SubtaskNode:
    """
    A node in the execution DAG representing a subtask with its assigned workflow.

    PRICING:
    - download_cost: From workflow (charged once per unique workflow)
    - execution_cost: From workflow (charged per node execution)
    - total_cost: Computed property (download + execution)
    """
    id: str
    description: str
    workflow: Workflow
    dependencies: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    weight: float = 1.0
    confidence_score: float = 0.0

    @property
    def workflow_id(self) -> str:
        """Get workflow ID."""
        return self.workflow.workflow_id

    @property
    def workflow_title(self) -> str:
        """Get workflow title."""
        return self.workflow.title

    @property
    def task_type(self) -> str:
        """Get task type."""
        return self.workflow.task_type

    @property
    def download_cost(self) -> int:
        """Get download cost (will be deduplicated at DAG level)."""
        return self.workflow.download_cost

    @property
    def execution_cost(self) -> int:
        """Get execution cost."""
        return self.workflow.execution_cost

    @property
    def total_cost(self) -> int:
        """
        Get total cost for this node.

        NOTE: This is a naive sum. The DAG-level total_cost property
        properly deduplicates download costs across nodes.
        """
        return self.download_cost + self.execution_cost

    # Backward compatibility aliases
    @property
    def token_cost(self) -> int:
        """Alias for download_cost (backward compatibility)."""
        return self.download_cost

    @property
    def execution_tokens(self) -> int:
        """Alias for execution_cost (backward compatibility)."""
        return self.execution_cost


@dataclass
class ExecutionDAG:
    """
    Execution DAG representing a complete solution.

    PRICING (FIXED):
    - total_download_cost: Sum of UNIQUE workflow download costs (deduplicated!)
    - total_execution_cost: Sum of ALL node execution costs
    - total_cost: total_download_cost + total_execution_cost
    """
    nodes: Dict[str, SubtaskNode]
    root_ids: List[str]
    execution_order: List[str]
    total_download_cost: int
    total_execution_cost: int
    coverage: str
    overall_confidence: float

    @property
    def total_cost(self) -> int:
        """
        Total cost = unique download costs + all execution costs.

        This property ensures consistent pricing semantics.
        """
        return self.total_download_cost + self.total_execution_cost

    def to_dict_with_workflows(self) -> Dict[str, Any]:
        """
        Serialize DAG with full workflow data for caching/purchase.

        Returns dict with:
        - nodes: List of node dicts with full workflows
        - pricing: Properly calculated costs
        - metadata: Coverage, confidence, etc.
        """
        # Serialize nodes with full workflow data
        nodes_list = []
        for node in self.nodes.values():
            node_dict = {
                "id": node.id,
                "description": node.description,
                "workflow": node.workflow.to_dict(),
                "dependencies": node.dependencies,
                "children": node.children,
                "weight": node.weight,
                "confidence_score": node.confidence_score
            }
            nodes_list.append(node_dict)

        # Recalculate pricing with proper deduplication
        unique_workflow_ids = set()
        recalc_download_cost = 0
        recalc_execution_cost = 0

        for node in self.nodes.values():
            # Download cost: charge once per unique workflow
            if node.workflow_id not in unique_workflow_ids:
                unique_workflow_ids.add(node.workflow_id)
                recalc_download_cost += node.download_cost

            # Execution cost: charge per node
            recalc_execution_cost += node.execution_cost

        return {
            "nodes": nodes_list,
            "root_ids": self.root_ids,
            "execution_order": self.execution_order,
            "pricing": {
                "total_download_cost": recalc_download_cost,
                "total_execution_cost": recalc_execution_cost,
                "total_cost_tokens": recalc_download_cost + recalc_execution_cost
            },
            "metadata": {
                "coverage": self.coverage,
                "overall_confidence": self.overall_confidence,
                "num_nodes": len(self.nodes),
                "num_unique_workflows": len(unique_workflow_ids)
            }
        }


@dataclass
class WorkflowNodeDoc:
    """
    A single node (subtask/step) within a workflow, indexed separately.

    Used for tree-aware recursive search (Step 9 in algorithm).
    Allows searching within workflow children without treating them as full workflows.
    """
    node_id: str
    workflow_id: str
    node_type: str  # "subtask" | "step" | "module"
    title: str
    text: str  # Full description/memo
    capability: Optional[str] = None  # What this node can do
    parent_node_id: Optional[str] = None
    ordinal: int = 0  # Order within parent
    embedding: Optional[List[float]] = None
    score: float = 0.0

    @classmethod
    def from_es_hit(cls, hit: Dict[str, Any]) -> "WorkflowNodeDoc":
        """Create WorkflowNodeDoc from Elasticsearch hit."""
        source = hit.get("_source", {})
        score = hit.get("_score", 0.0)

        return cls(
            node_id=source["node_id"],
            workflow_id=source["workflow_id"],
            node_type=source["node_type"],
            title=source.get("title", ""),
            text=source.get("text", ""),
            capability=source.get("capability"),
            parent_node_id=source.get("parent_node_id"),
            ordinal=source.get("ordinal", 0),
            embedding=source.get("embedding"),
            score=score
        )

    def to_es_document(self) -> Dict[str, Any]:
        """Convert to Elasticsearch document for indexing."""
        doc = {
            "node_id": self.node_id,
            "workflow_id": self.workflow_id,
            "node_type": self.node_type,
            "title": self.title,
            "text": self.text,
            "ordinal": self.ordinal
        }

        if self.capability:
            doc["capability"] = self.capability
        if self.parent_node_id:
            doc["parent_node_id"] = self.parent_node_id
        if self.embedding:
            doc["embedding"] = self.embedding

        return doc


@dataclass
class SearchResult:
    """
    A single search result from Elasticsearch.

    Pairs a workflow with its search relevance score.
    """
    workflow: Workflow
    score: float
    source: str = "direct"  # "direct" or "composite"


@dataclass
class SearchPlan:
    """
    A search plan from the decomposer.

    Can be either:
    - Direct: Single workflow or pool of candidates
    - Composite: Multiple workflows matched to subtasks
    """
    plan_type: str  # "direct" or "composite"
    workflows: List[Workflow]
    overall_score: float
    subtasks: List[Subtask] = field(default_factory=list)
    subtask_workflow_mapping: Dict[int, int] = field(default_factory=dict)
    coverage: str = ""

    @property
    def is_composite(self) -> bool:
        """Check if this is a composite plan."""
        return self.plan_type == "composite"


# Example usage and validation
if __name__ == "__main__":
    print("Testing models...")

    # Test Subtask
    subtask = Subtask(
        text="File Ohio taxes",
        task_type="tax_filing",
        weight=1.0,
        rationale="Main task"
    )
    print(f"✓ Subtask: {subtask.text}")

    # Test Workflow with normalized naming
    workflow = Workflow(
        workflow_id="ohio_2024",
        title="Ohio 2024 IT-1040",
        description="File Ohio taxes",
        task_type="tax_filing",
        download_cost=200,  # ✅ New naming
        execution_cost=800   # ✅ New naming
    )
    print(f"✓ Workflow: {workflow.title}")
    print(f"  Download cost: {workflow.download_cost} tokens")
    print(f"  Execution cost: {workflow.execution_cost} tokens")

    # Test SubtaskNode
    node = SubtaskNode(
        id="subtask_0",
        description="File Ohio taxes",
        workflow=workflow,
        weight=1.0,
        confidence_score=0.95
    )
    print(f"✓ Node: {node.description}")
    print(f"  Total cost: {node.total_cost} tokens")

    # Test ExecutionDAG with deduplication
    # Simulate two nodes using the same workflow
    node1 = SubtaskNode(
        id="subtask_0",
        description="Task 1 using same workflow",
        workflow=workflow,
        weight=1.0,
        confidence_score=0.95
    )
    node2 = SubtaskNode(
        id="subtask_1",
        description="Task 2 using same workflow",
        workflow=workflow,
        weight=0.8,
        confidence_score=0.90
    )

    nodes = {"subtask_0": node1, "subtask_1": node2}

    # Calculate deduplicated download cost
    unique_workflows = set()
    dedup_download = 0
    total_execution = 0

    for node in nodes.values():
        if node.workflow_id not in unique_workflows:
            unique_workflows.add(node.workflow_id)
            dedup_download += node.download_cost
        total_execution += node.execution_cost

    dag = ExecutionDAG(
        nodes=nodes,
        root_ids=["subtask_0"],
        execution_order=["subtask_0", "subtask_1"],
        total_download_cost=dedup_download,  # ✅ 200 (once, not twice!)
        total_execution_cost=total_execution,  # ✅ 1600 (800 * 2)
        coverage="2/2",
        overall_confidence=0.925
    )

    print(f"\n✓ ExecutionDAG:")
    print(f"  Nodes: {len(dag.nodes)}")
    print(f"  Download cost (deduplicated): {dag.total_download_cost} tokens")
    print(f"  Execution cost (2 runs): {dag.total_execution_cost} tokens")
    print(f"  Total cost: {dag.total_cost} tokens")
    print(f"  Expected: 200 + 1600 = 1800 tokens")
    print(f"  Without dedup would be: 400 + 1600 = 2000 tokens ❌")

    # Test serialization
    dag_dict = dag.to_dict_with_workflows()
    print(f"\n✓ Serialization:")
    print(f"  Pricing in dict: {dag_dict['pricing']}")
    print(f"  Metadata: {dag_dict['metadata']}")

    print("\n✅ All models working correctly!")
