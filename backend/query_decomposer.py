"""
Recursive query decomposer with scoring algorithm.

Algorithm:
1. Broad search on task_memo → candidates
2. Compute best_plan_score
3. If best_plan_score >= τ_good: return best
4. Else: subtasks = decompose(task_memo) (2-8 subtasks)
5. For each subtask: search → keep top 3
6. Compose best composite plan (pick best per subtask)
7. Score composite plan
8. If composite score improved by ≥ ε: accept
9. If composite still weak and depth < 2:
   - Pick worst-matching subtask
   - Split it once → search its children
   - Recompute composite
10. Return best plan found within budget
"""

from typing import List, Optional
from dataclasses import dataclass
import time

from config import Config, get_claude_service, get_elasticsearch_service, get_embedding_service
from workflow_loader import load_workflows_from_json, workflow_to_text, prepare_for_indexing, validate_workflow_consistency
from models import Workflow, SearchResult, Subtask, SearchPlan


@dataclass
class CompositePlan:
    """Composite plan from multiple subtasks."""
    workflows: List[Workflow]  # Best workflow per subtask (now uses Workflow model!)
    subtasks: List[Subtask]  # Subtasks that generated these
    overall_score: float
    coverage: str  # "N/M subtasks matched"


class RecursiveQueryDecomposer:
    """
    Recursive query decomposer implementing the scoring algorithm.
    """

    def __init__(self):
        """Initialize with all services."""
        self.claude_service = get_claude_service()
        self.es_service = get_elasticsearch_service()
        self.embedding_service = get_embedding_service()

        # Algorithm parameters from config
        self.score_threshold_good = Config.SCORE_THRESHOLD_GOOD
        self.score_improvement_epsilon = Config.SCORE_IMPROVEMENT_EPSILON
        self.max_recursion_depth = Config.MAX_RECURSION_DEPTH
        self.subtasks_min = Config.SUBTASKS_MIN
        self.subtasks_max = Config.SUBTASKS_MAX

        print("RecursiveQueryDecomposer initialized")
        print(f"  Score threshold (τ_good): {self.score_threshold_good}")
        print(f"  Improvement epsilon (ε): {self.score_improvement_epsilon}")
        print(f"  Max recursion depth: {self.max_recursion_depth}")

    def load_and_index_workflows(self, workflows_path: str):
        """
        Load workflows from JSON and index into Elasticsearch.

        Uses simplified workflow_loader that preserves workflows as-is without
        creating artificial tree structures for steps.

        Args:
            workflows_path: Path to workflows.json
        """
        print(f"\n{'='*60}")
        print(f"Loading and indexing workflows from {workflows_path}")
        print(f"{'='*60}\n")

        # Step 1: Load workflows directly
        print("[1/4] Loading workflows from JSON...")
        workflows = load_workflows_from_json(workflows_path)
        print(f"  ✓ Loaded {len(workflows)} workflows")

        # Step 2: Validate consistency
        print("\n[2/4] Validating workflow consistency...")
        total_errors = 0
        for workflow in workflows:
            errors = validate_workflow_consistency(workflow)
            if errors:
                print(f"  ⚠ Validation errors for {workflow.workflow_id}:")
                for error in errors:
                    print(f"    - {error}")
                total_errors += len(errors)

        if total_errors == 0:
            print(f"  ✓ All workflows valid")
        else:
            print(f"  ⚠ Found {total_errors} validation errors")

        # Step 3: Generate embeddings
        print("\n[3/4] Generating embeddings for all workflows...")
        documents = []

        for i, workflow in enumerate(workflows):
            # Create text representation
            full_text = workflow_to_text(workflow)

            # Generate embedding
            embedding = self.embedding_service.embed(full_text)

            # Prepare document for indexing
            doc = prepare_for_indexing(workflow, full_text, embedding)

            documents.append(doc)

            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{len(workflows)} embeddings...")

        print(f"  ✓ Generated embeddings for all {len(documents)} workflows")

        # Step 4: Bulk index into Elasticsearch
        print("\n[4/4] Indexing into Elasticsearch...")
        self.es_service.index_bulk(documents)

        print(f"\n{'='*60}")
        print(f"✓ Indexing complete! Indexed {len(documents)} workflows")
        print(f"{'='*60}\n")


    def search(
        self,
        task_description: str,
        top_k: int = 10,
        depth: int = 0
    ) -> SearchPlan:
        """
        Main search method implementing the recursive algorithm.

        Args:
            task_description: Natural language task description
            top_k: Number of results to return
            depth: Current recursion depth

        Returns:
            SearchPlan with either direct match or composite plan
        """
        print(f"\n{'='*60}")
        print(f"[Depth {depth}] Searching for: {task_description}")
        print(f"{'='*60}")

        # Step 1: Broad search on task
        print("\n[Step 1] Performing broad search...")
        candidates = self._broad_search(task_description, top_k=10)

        if not candidates:
            print("No candidates found")
            return SearchPlan(
                plan_type="direct",
                workflows=[],
                overall_score=0.0
            )

        # Step 2: Compute best plan score
        print("\n[Step 2] Scoring candidates...")
        best_candidate = max(candidates, key=lambda x: x.score)
        best_plan_score = self.claude_service.score_plan_quality(
            task_description,
            best_candidate.workflow
        )

        print(f"Best direct match: {best_candidate.workflow.title}")
        print(f"Best plan score: {best_plan_score:.3f} (threshold: {self.score_threshold_good})")

        # Step 3: If best_plan_score >= τ_good, return best
        if best_plan_score >= self.score_threshold_good:
            print(f"\n✓ Score above threshold! Returning direct match.")
            # Return direct match plan with pool of candidates
            workflows = [c.workflow for c in candidates[:top_k]]
            return SearchPlan(
                plan_type="direct",
                workflows=workflows,
                overall_score=best_plan_score
            )

        # Step 4: Decompose into subtasks
        print(f"\n[Step 3] Score below threshold. Decomposing into subtasks...")
        subtasks_dicts = self.claude_service.decompose_task(
            task_description,
            min_subtasks=self.subtasks_min,
            max_subtasks=self.subtasks_max
        )

        # Convert dicts to Subtask objects immediately
        subtasks = [Subtask.from_dict(st) for st in subtasks_dicts]

        print(f"Decomposed into {len(subtasks)} subtasks:")
        for i, st in enumerate(subtasks):
            print(f"  {i+1}. {st.text} (weight={st.weight}, type={st.task_type})")

        # Step 5-7: Search each subtask and compose plan
        print(f"\n[Step 4-6] Searching subtasks and composing plan...")
        composite_plan = self._compose_plan_from_subtasks(
            task_description,
            subtasks
        )

        print(f"\nComposite plan score: {composite_plan.overall_score:.3f}")
        print(f"Coverage: {composite_plan.coverage}")

        # Step 8: If composite improved by ≥ ε, accept
        improvement = composite_plan.overall_score - best_plan_score

        print(f"\nImprovement: {improvement:.3f} (epsilon: {self.score_improvement_epsilon})")

        if improvement >= self.score_improvement_epsilon:
            print(f"✓ Composite plan improved! Accepting.")
            return self._composite_to_plan(composite_plan)

        # Step 9: If still weak and depth < max, recursive split
        if composite_plan.overall_score < self.score_threshold_good and depth < self.max_recursion_depth:
            print(f"\n[Step 7] Composite still weak. Attempting recursive split (depth {depth+1})...")
            improved_plan = self._recursive_split(
                task_description,
                composite_plan,
                depth=depth + 1
            )

            if improved_plan and improved_plan.overall_score > composite_plan.overall_score:
                print(f"✓ Recursive split improved score to {improved_plan.overall_score:.3f}")
                return self._composite_to_plan(improved_plan)

        # Step 10: Return best plan found
        print(f"\n[Final] Returning best plan (score: {max(best_plan_score, composite_plan.overall_score):.3f})")

        if composite_plan.overall_score > best_plan_score:
            return self._composite_to_plan(composite_plan)
        else:
            # Return direct match
            workflows = [c.workflow for c in candidates[:top_k]]
            return SearchPlan(
                plan_type="direct",
                workflows=workflows,
                overall_score=best_plan_score
            )

    def _broad_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Perform broad search using hybrid search.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of SearchResult objects with Workflow models
        """
        # Generate embedding
        query_embedding = self.embedding_service.embed(query)

        # Hybrid search (returns list of dicts from Elasticsearch)
        results = self.es_service.hybrid_search(
            query_embedding=query_embedding,
            query_text=query,
            top_k=top_k
        )

        # Filter to workflows only (not steps) - check _source for node_type
        workflow_results = [r for r in results if r.get("_source", {}).get("node_type") == "workflow"]

        # Convert to SearchResult with Workflow models using from_es_hit
        search_results = []
        for hit in workflow_results:
            # Convert ES hit to Workflow object (handles _source and _score)
            workflow = Workflow.from_es_hit(hit)

            search_results.append(SearchResult(
                workflow=workflow,  # Now using Workflow model!
                score=hit.get("_score", 0.0),
                source="direct"
            ))

        return search_results

    def _compose_plan_from_subtasks(
        self,
        original_task: str,
        subtasks: List[Subtask]
    ) -> CompositePlan:
        """
        Search each subtask and compose best composite plan.

        Args:
            original_task: Original task description
            subtasks: List of subtask dicts

        Returns:
            CompositePlan
        """
        subtask_results = []  # List of (subtask, top_3_results)

        # Search each subtask
        for subtask in subtasks:
            subtask_query = subtask.text
            print(f"  Searching subtask: {subtask_query}")

            # Search with filters
            filters = {}
            if subtask.task_type and subtask.task_type != "general":
                filters["task_type"] = subtask.task_type

            embedding = self.embedding_service.embed(subtask_query)
            results = self.es_service.hybrid_search(
                query_embedding=embedding,
                query_text=subtask_query,
                filters=filters,
                top_k=3
            )

            # Filter to workflows and convert to Workflow objects using from_es_hit
            workflow_hits = [r for r in results if r.get("_source", {}).get("node_type") == "workflow"][:3]
            workflows = [Workflow.from_es_hit(hit) for hit in workflow_hits]

            if workflows:
                print(f"    Found {len(workflows)} results")
                subtask_results.append((subtask, workflows))
            else:
                print(f"    No results found")

        # Compose: pick best per subtask
        if not subtask_results:
            return CompositePlan(
                workflows=[],
                subtasks=subtasks,
                overall_score=0.0,
                coverage="0/{}".format(len(subtasks))
            )

        best_workflows = []
        matched_subtasks = []
        for subtask, results in subtask_results:
            # Pick best result for this subtask
            best = results[0]
            best_workflows.append(best)
            matched_subtasks.append(subtask)

        # Score composite plan
        # Simple scoring: average of individual scores weighted by subtask importance
        weighted_scores = []
        for subtask, workflow in zip(matched_subtasks, best_workflows):
            workflow_score = self.claude_service.score_plan_quality(
                subtask.text,
                workflow
            )
            weighted_score = workflow_score * subtask.weight
            weighted_scores.append(weighted_score)

        # Overall score: weighted average
        total_weight = sum(st.weight for st in matched_subtasks)
        overall_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0.0

        return CompositePlan(
            workflows=best_workflows,
            subtasks=matched_subtasks,
            overall_score=overall_score,
            coverage=f"{len(matched_subtasks)}/{len(subtasks)}"
        )

    def _recursive_split(
        self,
        original_task: str,
        composite_plan: CompositePlan,
        depth: int
    ) -> Optional[CompositePlan]:
        """
        Recursively split worst-matching subtask.

        Args:
            original_task: Original task
            composite_plan: Current composite plan
            depth: Current depth

        Returns:
            Improved CompositePlan or None
        """
        # Find worst-matching subtask
        worst_idx = -1
        worst_score = 1.0

        for i, (subtask, workflow) in enumerate(zip(composite_plan.subtasks, composite_plan.workflows)):
            score = self.claude_service.score_plan_quality(subtask.text, workflow)
            if score < worst_score:
                worst_score = score
                worst_idx = i

        if worst_idx == -1:
            return None

        worst_subtask = composite_plan.subtasks[worst_idx]
        print(f"  Worst subtask: {worst_subtask.text} (score={worst_score:.3f})")

        # Recursively search worst subtask
        print(f"  Recursively splitting...")
        recursive_plan = self.search(
            task_description=worst_subtask.text,
            top_k=3,
            depth=depth
        )

        if not recursive_plan.workflows:
            return None

        # Replace worst subtask result with best workflow from recursive search
        improved_workflows = composite_plan.workflows.copy()
        improved_workflows[worst_idx] = recursive_plan.workflows[0]

        # Recompute score
        weighted_scores = []
        for subtask, workflow in zip(composite_plan.subtasks, improved_workflows):
            workflow_score = self.claude_service.score_plan_quality(
                subtask.text,
                workflow
            )
            weighted_score = workflow_score * subtask.weight
            weighted_scores.append(weighted_score)

        total_weight = sum(st.weight for st in composite_plan.subtasks)
        new_overall_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0.0

        return CompositePlan(
            workflows=improved_workflows,
            subtasks=composite_plan.subtasks,
            overall_score=new_overall_score,
            coverage=composite_plan.coverage
        )

    def _composite_to_plan(self, composite_plan: CompositePlan) -> SearchPlan:
        """
        Convert CompositePlan to SearchPlan with explicit subtask->workflow mapping.

        This preserves the decomposer's careful matching so recomposer can use it directly.
        """
        # Create mapping: subtask index -> workflow index
        subtask_workflow_mapping = {}
        for i in range(len(composite_plan.subtasks)):
            subtask_workflow_mapping[i] = i  # 1-to-1 mapping

        return SearchPlan(
            plan_type="composite",
            workflows=composite_plan.workflows,
            overall_score=composite_plan.overall_score,
            subtasks=composite_plan.subtasks,
            subtask_workflow_mapping=subtask_workflow_mapping,
            coverage=composite_plan.coverage
        )


# Example usage
if __name__ == "__main__":
    from config import initialize_services

    # Initialize services
    print("=== Initializing Services ===")
    initialize_services()

    # Create decomposer
    decomposer = RecursiveQueryDecomposer()

    # Test query
    test_query = "I need to file my Ohio 2024 taxes with W2 income and itemized deductions"

    print(f"\n=== Testing Recursive Search ===")
    print(f"Query: {test_query}\n")

    start_time = time.time()
    search_plan = decomposer.search(test_query, top_k=5)
    elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"FINAL RESULTS (took {elapsed:.2f}s)")
    print(f"{'='*60}\n")

    print(f"Plan type: {search_plan.plan_type}")
    print(f"Overall score: {search_plan.overall_score:.3f}")
    print(f"Workflows found: {len(search_plan.workflows)}\n")

    for i, workflow in enumerate(search_plan.workflows):
        print(f"{i+1}. {workflow.title}")
        print(f"   Workflow ID: {workflow.workflow_id}")
        print(f"   Task type: {workflow.task_type}")
        print(f"   Cost: {workflow.total_cost} tokens")
        print()

    if search_plan.is_composite:
        print("Composite plan details:")
        print(f"  Coverage: {search_plan.coverage}")
        print(f"  Subtasks: {len(search_plan.subtasks)}")
        if search_plan.subtask_workflow_mapping:
            print(f"  Mappings:")
            for st_idx, wf_idx in search_plan.subtask_workflow_mapping.items():
                subtask = search_plan.subtasks[st_idx]
                workflow = search_plan.workflows[wf_idx]
                print(f"    {st_idx}. '{subtask.text}' → {workflow.title}")
