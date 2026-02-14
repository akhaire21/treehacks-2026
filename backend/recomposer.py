"""
Recomposer: Builds DAG (Directed Acyclic Graph) of subtasks from search results.

Takes decomposed subtasks + matched workflows and constructs an execution DAG
with dependencies, pricing, and execution order.

Uses unified models from models.py - NO DICTS!
"""

from typing import List, Dict, Optional

from models import Workflow, SubtaskNode, ExecutionDAG, Subtask, SearchPlan


class WorkflowRecomposer:
    """
    Recomposes search results into an execution DAG.

    Now uses unified models instead of dicts!
    """

    def __init__(self):
        """Initialize recomposer."""
        print("WorkflowRecomposer initialized")

    def recompose(
        self,
        subtasks: List[Subtask],  # ✅ Was: List[Dict]
        search_plan: SearchPlan,  # ✅ NEW: Was List[SearchResult]
        top_k: int = 5
    ) -> List[ExecutionDAG]:
        """
        Build multiple execution DAG solutions from subtasks and search plan.

        Args:
            subtasks: List of Subtask objects from LLM decomposition
            search_plan: SearchPlan from decomposer (direct or composite)
            top_k: Number of DAG solutions to generate

        Returns:
            List of ExecutionDAG solutions, ranked by confidence and cost
        """
        print(f"\n{'='*60}")
        print(f"Recomposing {len(subtasks)} subtasks into {top_k} DAG solutions")
        print(f"Plan type: {search_plan.plan_type}")
        print(f"{'='*60}\n")

        # Generate multiple DAG solutions by trying different workflow combinations
        dag_solutions = []

        # If composite plan, use the decomposer's mapping directly
        if search_plan.is_composite:
            print("Using composite plan with explicit subtask->workflow mappings")
            dag1 = self._create_dag_from_composite(search_plan)
            if dag1:
                dag_solutions.append(dag1)

            # Also try alternative combinations for diversity
            if len(search_plan.workflows) > 1:
                dag2 = self._create_single_workflow_dag_from_plan(search_plan)
                if dag2:
                    dag_solutions.append(dag2)
        else:
            # Direct plan: use workflows as a pool
            print("Using direct plan - generating multiple DAG strategies")

            # Strategy 1: Best single workflow covering all subtasks
            dag1 = self._create_single_workflow_dag_from_plan(search_plan)
            if dag1:
                dag_solutions.append(dag1)

            # Strategy 2: Separate workflows per subtask (if enough results)
            if len(search_plan.workflows) >= len(subtasks):
                dag2 = self._create_multi_workflow_dag_from_plan(subtasks, search_plan)
                if dag2:
                    dag_solutions.append(dag2)

            # Strategy 3-K: Variations with different workflow assignments
            for i in range(2, min(top_k, len(search_plan.workflows))):
                dag_variant = self._create_variant_dag_from_plan(search_plan, variant=i)
                if dag_variant:
                    dag_solutions.append(dag_variant)

        # Rank by combined score (confidence + cost efficiency)
        dag_solutions = self._rank_dags(dag_solutions)[:top_k]

        print(f"✓ Generated {len(dag_solutions)} DAG solutions")
        for i, dag in enumerate(dag_solutions):
            print(f"  Solution {i+1}: {dag.total_cost} tokens, confidence={dag.overall_confidence:.2f}")

        return dag_solutions

    def _create_dag_from_composite(self, search_plan: SearchPlan) -> Optional[ExecutionDAG]:
        """
        Create DAG from composite plan using decomposer's subtask->workflow mappings.

        This respects the careful matching done by the decomposer.
        """
        if not search_plan.subtasks or not search_plan.subtask_workflow_mapping:
            return None

        # Create nodes using the explicit mapping
        nodes = {}
        matched_subtasks = []  # Only subtasks that have workflows

        for subtask_idx, workflow_idx in search_plan.subtask_workflow_mapping.items():
            subtask = search_plan.subtasks[subtask_idx]
            workflow = search_plan.workflows[workflow_idx]

            subtask_id = f"subtask_{subtask_idx}"
            node = SubtaskNode(
                id=subtask_id,
                description=subtask.text,
                workflow=workflow,
                weight=subtask.weight,
                confidence_score=workflow.similarity_score
            )
            nodes[subtask_id] = node
            matched_subtasks.append(subtask)

        # Infer dependencies using only matched subtasks
        self._infer_dependencies(nodes, matched_subtasks)

        # Topological sort
        execution_order = self._topological_sort(nodes)

        # Root nodes
        root_ids = [nid for nid, node in nodes.items() if not node.dependencies]

        # Sum pricing
        total_download = sum(node.token_cost for node in nodes.values())
        total_execution = sum(node.execution_tokens for node in nodes.values())

        # Confidence
        overall_confidence = (
            sum(node.confidence_score * node.weight for node in nodes.values()) /
            sum(node.weight for node in nodes.values())
            if nodes else 0.0
        )

        return ExecutionDAG(
            nodes=nodes,
            root_ids=root_ids,
            execution_order=execution_order,
            total_download_cost=total_download,
            total_execution_cost=total_execution,
            coverage=search_plan.coverage or f"{len(nodes)}/{len(search_plan.subtasks)}",
            overall_confidence=overall_confidence
        )

    def _create_single_workflow_dag_from_plan(
        self,
        search_plan: SearchPlan
    ) -> Optional[ExecutionDAG]:
        """Create DAG using best single workflow for all subtasks."""
        if not search_plan.workflows:
            return None

        best_workflow = search_plan.workflows[0]

        # Create one node representing the entire workflow
        node = SubtaskNode(
            id="subtask_0",
            description="Complete workflow",
            workflow=best_workflow,
            weight=1.0,
            confidence_score=best_workflow.similarity_score
        )

        nodes = {"subtask_0": node}

        return ExecutionDAG(
            nodes=nodes,
            root_ids=["subtask_0"],
            execution_order=["subtask_0"],
            total_download_cost=node.token_cost,
            total_execution_cost=node.execution_tokens,
            coverage=f"1/1",
            overall_confidence=node.confidence_score
        )

    def _create_multi_workflow_dag_from_plan(
        self,
        subtasks: List[Subtask],
        search_plan: SearchPlan
    ) -> Optional[ExecutionDAG]:
        """Create DAG using separate workflow for each subtask."""
        # Match each subtask to best workflow from the pool
        # Returns (subtask_idx, subtask, workflow) to preserve original indices
        matched_triples = self._match_subtasks_to_workflows_from_pool(
            subtasks,
            search_plan.workflows
        )

        if not matched_triples:
            return None

        # Create nodes for each subtask, preserving original indices
        nodes = {}
        matched_subtasks = []

        for subtask_idx, subtask, workflow in matched_triples:
            subtask_id = f"subtask_{subtask_idx}"  # ✅ Use original index

            # Create SubtaskNode with Workflow object
            node = SubtaskNode(
                id=subtask_id,
                description=subtask.text,
                workflow=workflow,
                weight=subtask.weight,
                confidence_score=workflow.similarity_score
            )

            nodes[subtask_id] = node
            matched_subtasks.append(subtask)

        # Infer dependencies using only matched subtasks
        self._infer_dependencies(nodes, matched_subtasks)

        # Topological sort
        execution_order = self._topological_sort(nodes)

        # Root nodes
        root_ids = [nid for nid, node in nodes.items() if not node.dependencies]

        # Sum pricing across all subtasks
        total_download = sum(node.token_cost for node in nodes.values())
        total_execution = sum(node.execution_tokens for node in nodes.values())

        # Coverage
        coverage = f"{len(matched_triples)}/{len(subtasks)}"

        # Confidence
        overall_confidence = (
            sum(node.confidence_score * node.weight for node in nodes.values()) /
            sum(node.weight for node in nodes.values())
            if nodes else 0.0
        )

        return ExecutionDAG(
            nodes=nodes,
            root_ids=root_ids,
            execution_order=execution_order,
            total_download_cost=total_download,
            total_execution_cost=total_execution,
            coverage=coverage,
            overall_confidence=overall_confidence
        )

    def _create_variant_dag_from_plan(
        self,
        search_plan: SearchPlan,
        variant: int
    ) -> Optional[ExecutionDAG]:
        """Create DAG variant using different workflow combinations."""
        if variant >= len(search_plan.workflows):
            return None

        # Use a different workflow for the main task
        main_workflow = search_plan.workflows[min(variant, len(search_plan.workflows) - 1)]

        node = SubtaskNode(
            id="subtask_0",
            description="Main workflow",
            workflow=main_workflow,
            weight=1.0,
            confidence_score=main_workflow.similarity_score
        )

        nodes = {"subtask_0": node}

        return ExecutionDAG(
            nodes=nodes,
            root_ids=["subtask_0"],
            execution_order=["subtask_0"],
            total_download_cost=node.token_cost,
            total_execution_cost=node.execution_tokens,
            coverage="1/1",
            overall_confidence=node.confidence_score
        )

    def _rank_dags(self, dags: List[ExecutionDAG]) -> List[ExecutionDAG]:
        """Rank DAGs by combined score (confidence + cost efficiency)."""
        def score_dag(dag: ExecutionDAG) -> float:
            # Higher confidence = better
            # Lower cost = better
            confidence_score = dag.overall_confidence * 10
            cost_score = max(0, 10 - (dag.total_cost / 1000))
            return confidence_score + cost_score

        return sorted(dags, key=score_dag, reverse=True)

    def _match_subtasks_to_workflows_from_pool(
        self,
        subtasks: List[Subtask],
        workflows: List[Workflow],
        embedding_service=None
    ) -> List[tuple]:
        """
        Match each subtask to its best workflow from a pool of workflows.

        Returns:
            List of (subtask_idx, subtask, workflow) triples to preserve original indices
        """
        from config import get_embedding_service

        if embedding_service is None:
            embedding_service = get_embedding_service()

        matched_triples = []

        for subtask_idx, subtask in enumerate(subtasks):
            best_workflow = None
            best_score = -1

            # Generate embedding for subtask
            subtask_embedding = embedding_service.embed(subtask.text)

            for workflow in workflows:
                # Use embedding similarity if available
                if workflow.embedding:
                    similarity = embedding_service.cosine_similarity(
                        subtask_embedding,
                        workflow.embedding
                    )
                    score = similarity
                else:
                    # Fallback: use existing similarity score
                    score = workflow.similarity_score

                # Boost if task types match
                if workflow.task_type == subtask.task_type:
                    score *= 1.2

                if score > best_score:
                    best_score = score
                    best_workflow = workflow

            if best_workflow:
                matched_triples.append((subtask_idx, subtask, best_workflow))
                print(f"  Matched [{subtask_idx}]: '{subtask.text}' → {best_workflow.title} (score={best_score:.3f})")
            else:
                print(f"  Warning: No workflow found for subtask [{subtask_idx}] '{subtask.text}'")

        return matched_triples

    def _infer_dependencies(
        self,
        nodes: Dict[str, SubtaskNode],
        subtasks: List[Subtask]
    ):
        """
        Infer dependencies between subtasks based on task types and weights.

        Rules:
        - Main tasks (weight=1.0) have no dependencies
        - Lower weight tasks depend on higher weight tasks
        """
        node_list = list(nodes.values())

        for i, node in enumerate(node_list):
            # Main tasks (weight >= 0.9) are roots
            if node.weight >= 0.9:
                continue

            # Find potential parents (higher weight or earlier in list)
            for j, potential_parent in enumerate(node_list):
                if i == j:
                    continue

                # Add dependency if parent has higher weight or comes before
                if potential_parent.weight > node.weight or j < i:
                    if potential_parent.id not in node.dependencies:
                        node.dependencies.append(potential_parent.id)
                        potential_parent.children.append(node.id)

    def _topological_sort(self, nodes: Dict[str, SubtaskNode]) -> List[str]:
        """
        Topologically sort nodes for execution order.

        Returns:
            List of node IDs in execution order
        """
        # Kahn's algorithm
        in_degree = {node_id: len(node.dependencies) for node_id, node in nodes.items()}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_order = []

        while queue:
            # Sort by weight (descending) to prioritize important tasks
            queue.sort(key=lambda nid: nodes[nid].weight, reverse=True)
            node_id = queue.pop(0)
            sorted_order.append(node_id)

            # Reduce in-degree for children
            for child_id in nodes[node_id].children:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        # Check for cycles
        if len(sorted_order) != len(nodes):
            print("Warning: Cycle detected in DAG!")
            return list(nodes.keys())

        return sorted_order


# Example usage
if __name__ == "__main__":
    from models import Workflow, Subtask, SearchPlan

    # Mock subtasks
    subtasks = [
        Subtask(text="Ohio state tax filing", task_type="tax_filing", weight=1.0, rationale="Primary task"),
        Subtask(text="W2 income reporting", task_type="requirements", weight=0.7, rationale="Income type")
    ]

    # Mock workflow
    workflow = Workflow(
        workflow_id="ohio_w2_itemized_2024",
        title="Ohio 2024 IT-1040 (W2, Itemized)",
        description="File Ohio taxes",
        task_type="tax_filing",
        token_cost=200,
        execution_tokens=800
    )

    # Mock search plan (direct)
    search_plan = SearchPlan(
        plan_type="direct",
        workflows=[workflow],
        overall_score=0.92
    )

    # Recompose
    recomposer = WorkflowRecomposer()
    dags = recomposer.recompose(subtasks, search_plan, top_k=3)

    # Print DAG
    print(f"\n✓ Generated {len(dags)} DAG solutions")
    for i, dag in enumerate(dags):
        print(f"\nSolution {i+1}:")
        print(f"  Total cost: {dag.total_cost} tokens")
        print(f"  Confidence: {dag.overall_confidence:.2f}")
        print(f"  Nodes: {len(dag.nodes)}")
