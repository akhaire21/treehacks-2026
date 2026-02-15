"""
End-to-end orchestrator for the agent marketplace.

═══════════════════════════════════════════════════════════════════════════════
ORCHESTRATION PIPELINE
═══════════════════════════════════════════════════════════════════════════════

This orchestrator implements a two-phase marketplace interaction:

Phase 1: ESTIMATE (GET /api/estimate)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Sanitize Query                                                            │
│    └─ Remove PII (names, SSN, exact income)                                  │
│    └─ Keep metadata (state, year, form types)                                │
│                                                                               │
│ 2. Search for Workflows (Elasticsearch + Recursive Algorithm)                │
│    └─ Hybrid search: semantic (embeddings) + keyword (text)                  │
│    └─ Recursive decomposition if needed (decomposer owns this!)              │
│    └─ Returns: SearchPlan with workflows and subtasks (single source!)       │
│                                                                               │
│ 3. Recompose into Multiple Execution DAGs                                    │
│    └─ Generate 3-5 solution candidates                                       │
│    └─ Each DAG: different workflow combinations                              │
│    └─ Match subtasks to workflows, infer dependencies                        │
│    └─ Calculate aggregate pricing and confidence                             │
│                                                                               │
│ 4. Return Solution Summaries                                                 │
│    └─ Multiple solutions ranked by confidence and cost                       │
│    └─ Summary only (NO workflow details yet)                                 │
│    └─ Cache full DAGs for purchase                                           │
│    └─ Return session_id for Phase 2                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 2: PURCHASE (POST /api/buy)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Retrieve Cached Solution                                                  │
│    └─ Use session_id and solution_id from Phase 1                            │
│                                                                               │
│ 2. Extract Full Workflow Details                                             │
│    └─ Get steps, edge_cases, domain_knowledge                                │
│    └─ This is what the agent pays for!                                       │
│                                                                               │
│ 3. Return Execution Plan                                                     │
│    └─ Full workflows with dependencies                                       │
│    └─ Execution order (topological sort)                                     │
│    └─ Purchase receipt with pricing                                          │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
KEY CONCEPTS
═══════════════════════════════════════════════════════════════════════════════

Workflow (Template)
├─ What exists in the marketplace
├─ Reusable template with steps and domain knowledge
└─ Analogy: Recipe in a cookbook

ExecutionDAG (Solution)
├─ How to solve a specific user query
├─ Composed of multiple workflows with dependencies
└─ Analogy: Meal plan combining multiple recipes

Privacy-First Architecture
├─ PII never sent to marketplace or indexed
├─ Agent keeps private data locally
└─ Only sanitized queries used for search

Multi-Solution Approach
├─ Generate 3-5 solution candidates
├─ Agent reviews pricing before purchase
└─ Flexibility to choose best cost/confidence tradeoff

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Any, Optional

from sanitizer import PrivacySanitizer
from query_decomposer import RecursiveQueryDecomposer
from recomposer import WorkflowRecomposer
from config import get_claude_service
from services.cache_service import get_cache_service
from models import Subtask, ExecutionDAG, SubtaskNode, Workflow


class MarketplaceOrchestrator:
    """
    End-to-end orchestrator for agent marketplace.

    Handles the complete pipeline from raw query to execution DAG.
    """

    def __init__(self):
        """Initialize orchestrator with all components."""
        self.sanitizer = PrivacySanitizer()
        self.decomposer = RecursiveQueryDecomposer()
        self.recomposer = WorkflowRecomposer()
        self.claude_service = get_claude_service()
        self.cache_service = get_cache_service()

        print("MarketplaceOrchestrator initialized")

    def estimate_price_and_search(
        self,
        raw_query: str,
        raw_context: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        require_close_match: bool = False
    ) -> Dict[str, Any]:
        """
        Estimate pricing and search for solution (no purchase yet).

        This is the first API endpoint that agents call to get:
        - Pricing estimate
        - Execution DAG
        - Solution overview

        Args:
            raw_query: Natural language query from agent
            raw_context: Optional context dict with metadata (may contain PII)
            top_k: Number of workflow candidates to return
            require_close_match: If True, return nothing if best score after max_depth
                                is below MIN_ACCEPTABLE_SCORE threshold (quality control)

        Returns:
            MarketplaceResponse with DAG and pricing (or empty if require_close_match=True
            and no good matches found)
        """
        print(f"\n{'='*70}")
        print(f"ESTIMATE PRICE AND SEARCH")
        print(f"{'='*70}\n")

        # STEP 1: Sanitize query (remove PII)
        print("[1/5] Sanitizing query...")
        if raw_context:
            sanitized_context, private_data = self.sanitizer.sanitize_query(raw_context)
        else:
            sanitized_context = {}
            private_data = {}

        # Also sanitize the query text itself
        sanitized_query_text = self.sanitizer.remove_pii_from_text(raw_query)

        sanitized_query = {
            "query": sanitized_query_text,
            **sanitized_context
        }

        print(f"  ✓ Sanitized (removed {len(private_data)} private fields)")
        print(f"  Public query: {sanitized_query_text}")

        # STEP 2: Search for workflows using recursive algorithm
        # NOTE: Decomposition happens inside decomposer if needed (single source of truth)
        print("\n[2/4] Searching for workflows...")
        search_plan = self.decomposer.search(
            task_description=sanitized_query_text,
            top_k=top_k,
            depth=0
        )

        print(f"  ✓ Search complete: {search_plan.plan_type} plan with {len(search_plan.workflows)} workflows")
        if search_plan.is_composite:
            print(f"  ✓ Composite plan coverage: {search_plan.coverage}")
        print(f"  ✓ Overall score: {search_plan.overall_score:.3f}")
        print(f"  ✓ Final depth: {search_plan.final_depth}, Max depth reached: {search_plan.max_depth_reached}")

        # ═══════════════════════════════════════════════════════════════════
        # QUALITY CONTROL: Check if results meet minimum acceptable score
        # ═══════════════════════════════════════════════════════════════════
        if require_close_match:
            from config import Config
            min_score = Config.MIN_ACCEPTABLE_SCORE

            if search_plan.max_depth_reached and search_plan.overall_score < min_score:
                print(f"\n⚠️  QUALITY CONTROL TRIGGERED")
                print(f"  Max depth reached: {search_plan.final_depth}")
                print(f"  Best score: {search_plan.overall_score:.3f}")
                print(f"  Required: {min_score:.3f}")
                print(f"  → Returning empty results (no close matches found)")

                return {
                    "query": {
                        "sanitized": sanitized_query,
                        "privacy_protected": True
                    },
                    "decomposition": {
                        "num_subtasks": len(search_plan.subtasks) if search_plan.subtasks else 1,
                        "subtasks": [st.to_dict() for st in search_plan.subtasks] if search_plan.subtasks else []
                    },
                    "solutions": [],
                    "num_solutions": 0,
                    "session_id": None,
                    "quality_control": {
                        "triggered": True,
                        "reason": "No close matches found after exhausting max recursion depth",
                        "max_depth_reached": True,
                        "final_depth": search_plan.final_depth,
                        "best_score": search_plan.overall_score,
                        "min_required_score": min_score
                    }
                }

        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL: Extract subtasks from search_plan (SINGLE SOURCE OF TRUTH!)
        # ═══════════════════════════════════════════════════════════════════
        # The decomposer owns decomposition. We use its subtasks everywhere:
        # 1. In recomposer to build DAGs
        # 2. In API response to show user
        # This ensures user sees EXACTLY what is executed (no divergence!)
        # ═══════════════════════════════════════════════════════════════════
        if search_plan.is_composite and search_plan.subtasks:
            subtasks = search_plan.subtasks
            print(f"  ✓ Using {len(subtasks)} subtasks from decomposer")
        else:
            # Direct plan: create a single subtask for the entire query
            subtasks = [Subtask(
                text=sanitized_query_text,
                task_type="general",
                weight=1.0,
                rationale="Direct match - no decomposition needed"
            )]
            print(f"  ✓ Direct plan: using single subtask")

        # STEP 3: Recompose into multiple execution DAG solutions
        print("\n[3/4] Recomposing into execution DAG solutions...")
        dag_solutions = self.recomposer.recompose(
            subtasks=subtasks,  # ✅ List[Subtask] from decomposer
            search_plan=search_plan,  # ✅ SearchPlan (was List[SearchResult])
            top_k=top_k
        )

        print(f"  ✓ Generated {len(dag_solutions)} solution candidates")

        # STEP 4: Return multiple solutions (summaries only, no full workflows)
        print("\n[4/4] Preparing solution summaries...")

        solutions = []
        for i, dag in enumerate(dag_solutions):
            # Estimate cost "from scratch" based on workflow metadata
            # Use token_comparison from workflow if available, else use heuristic
            from_scratch_estimate = self._estimate_from_scratch_cost(dag)
            savings_vs_scratch = from_scratch_estimate - dag.total_cost
            savings_percentage = int((savings_vs_scratch / from_scratch_estimate) * 100) if from_scratch_estimate > 0 else 0

            # Create solution summary (NO full workflow details)
            solution_summary = {
                "solution_id": f"sol_{i+1}",
                "rank": i + 1,
                "confidence_score": dag.overall_confidence,
                "pricing": {
                    "total_cost_tokens": dag.total_cost,
                    "download_cost": dag.total_download_cost,
                    "execution_cost": dag.total_execution_cost,
                    "from_scratch_estimate": from_scratch_estimate,
                    "savings_tokens": savings_vs_scratch,
                    "savings_percentage": savings_percentage
                },
                "structure": {
                    "num_workflows": len(dag.nodes),
                    "num_subtasks": len(subtasks),
                    "coverage": dag.coverage,
                    "execution_order": dag.execution_order
                },
                "workflows_summary": [
                    {
                        "workflow_id": node.workflow_id,
                        "workflow_title": node.workflow_title,
                        "task_type": node.task_type,
                        "subtask_description": node.description,
                        "token_cost": node.total_cost
                    }
                    for node in dag.nodes.values()
                ],
                # Store full DAG as serializable dict for purchase
                "_full_dag_dict": dag.to_dict_with_workflows()  # ✅ Serialize to dict!
            }

            solutions.append(solution_summary)

            print(f"  Solution {i+1}: {dag.total_cost} tokens ({savings_percentage}% savings)")

        # Cache solutions for buy endpoint (with serialized DAGs)
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:16]}"  # ✅ Use UUID for security
        self.cache_service.cache_solution(session_id, solutions)

        # Create response with multiple solutions (no _internal field)
        response = {
            "query": {
                "sanitized": sanitized_query,
                "privacy_protected": True
            },
            "decomposition": {
                "num_subtasks": len(subtasks),
                "subtasks": [st.to_dict() for st in subtasks]  # ✅ Convert to dicts for API
            },
            "solutions": [
                {k: v for k, v in sol.items() if k != "_full_dag_dict"}  # ✅ Hide serialized DAG
                for sol in solutions
            ],
            "num_solutions": len(solutions),
            "session_id": session_id
        }

        print(f"\n{'='*70}")
        print(f"✓ ESTIMATE COMPLETE - {len(solutions)} solutions available")
        print(f"{'='*70}\n")

        return response

    def buy_solution(
        self,
        session_id: str,
        solution_id: str
    ) -> Dict[str, Any]:
        """
        Purchase solution and return executable workflows.

        This is the second API endpoint that agents call after reviewing pricing.

        Args:
            session_id: Session ID from estimate_price_and_search
            solution_id: Which solution to buy (e.g., "sol_1", "sol_2")

        Returns:
            Dict with full workflow details for execution
        """
        print(f"\n{'='*70}")
        print(f"BUY SOLUTION")
        print(f"{'='*70}\n")

        print(f"[1/3] Retrieving solution {solution_id} from session {session_id}...")

        # Get cached solutions
        solutions = self.cache_service.get_solution(session_id)
        if not solutions:
            raise ValueError(f"Session {session_id} not found. Call /api/estimate first.")

        # Find selected solution
        selected_solution = None
        for sol in solutions:
            if sol["solution_id"] == solution_id:
                selected_solution = sol
                break

        if not selected_solution:
            raise ValueError(f"Solution {solution_id} not found in session {session_id}")

        # Deserialize DAG from dict
        dag_dict = selected_solution["_full_dag_dict"]

        # Reconstruct ExecutionDAG from dict
        nodes = {}
        for node_dict in dag_dict["nodes"]:
            workflow = Workflow.from_dict(node_dict["workflow"])
            node = SubtaskNode(
                id=node_dict["id"],
                description=node_dict["description"],
                workflow=workflow,
                dependencies=node_dict.get("dependencies", []),
                children=node_dict.get("children", []),
                weight=node_dict.get("weight", 1.0),
                confidence_score=node_dict.get("confidence_score", 0.0)
            )
            nodes[node.id] = node

        execution_dag = ExecutionDAG(
            nodes=nodes,
            root_ids=dag_dict["root_ids"],
            execution_order=dag_dict["execution_order"],
            total_download_cost=dag_dict["pricing"]["total_download_cost"],
            total_execution_cost=dag_dict["pricing"]["total_execution_cost"],
            coverage=dag_dict["metadata"]["coverage"],
            overall_confidence=dag_dict["metadata"]["overall_confidence"]
        )

        print(f"  ✓ Found solution: {execution_dag.total_cost} tokens, {len(execution_dag.nodes)} workflows")

        # Extract full workflow data for each subtask
        print(f"\n[2/3] Packaging full workflows...")
        purchased_workflows = []

        for node_id in execution_dag.execution_order:
            node = execution_dag.nodes[node_id]

            # Get full workflow data (this is what agent pays for!)
            workflow_data = node.workflow.to_dict()

            # Package for execution
            executable_subtask = {
                "subtask_id": node.id,
                "description": node.description,
                "workflow_id": node.workflow_id,
                "workflow_title": node.workflow_title,

                # Execution details
                "dependencies": node.dependencies,
                "children": node.children,

                # FULL workflow (steps, edge cases, domain knowledge, etc.)
                "workflow": workflow_data,

                # Pricing (for tracking)
                "tokens_charged": node.total_cost
            }

            purchased_workflows.append(executable_subtask)

        print(f"  ✓ Packaged {len(purchased_workflows)} workflows with full details")

        # Create purchase record
        print(f"\n[3/3] Finalizing purchase...")

        import uuid
        purchase_id = f"purchase_{uuid.uuid4().hex[:8]}"

        purchase_receipt = {
            "purchase_id": purchase_id,
            "session_id": session_id,
            "solution_id": solution_id,
            "timestamp": "2024-02-14T12:00:00Z",  # Use actual timestamp in production
            "tokens_charged": execution_dag.total_cost,
            "num_workflows": len(purchased_workflows),
            "execution_plan": {
                "execution_order": execution_dag.execution_order,
                "root_ids": execution_dag.root_ids,
                "workflows": purchased_workflows
            },
            "status": "purchased",
            "usage_instructions": {
                "1": "Execute workflows in the order specified by execution_order",
                "2": "Pass private data (kept locally) to each workflow during execution",
                "3": "Each workflow contains steps, edge_cases, and domain_knowledge",
                "4": "Follow the 'steps' array sequentially for each workflow"
            }
        }

        print(f"  ✓ Purchase complete!")
        print(f"  ✓ Purchase ID: {purchase_id}")
        print(f"  ✓ Tokens charged: {execution_dag.total_cost}")

        print(f"\n{'='*70}")
        print(f"✓ PURCHASE COMPLETE")
        print(f"{'='*70}\n")

        return purchase_receipt

    def _estimate_from_scratch_cost(self, dag) -> int:
        """
        Estimate cost to solve from scratch without marketplace.

        Uses workflow metadata if available, otherwise uses heuristic.
        """
        total_from_scratch = 0

        for node in dag.nodes.values():
            workflow = node.workflow  # ✅ It's a Workflow object now!

            # Check if workflow has token_comparison metadata
            if workflow and workflow.token_comparison:
                from_scratch_tokens = workflow.token_comparison.from_scratch
                if from_scratch_tokens > 0:
                    total_from_scratch += from_scratch_tokens
                    continue

            # Fallback heuristic: 3-5x the workflow cost based on complexity
            # More complex workflows (more steps) have higher multiplier
            num_steps = len(workflow.steps) if workflow else 10
            multiplier = 3 + min(2, num_steps / 10)  # 3x to 5x based on steps
            total_from_scratch += int(node.total_cost * multiplier)

        return total_from_scratch


# Example usage
if __name__ == "__main__":
    from config import initialize_services

    # Initialize services
    print("Initializing services...")
    initialize_services()

    # Create orchestrator
    orchestrator = MarketplaceOrchestrator()

    # Load and index workflows (one-time setup)
    print("\nLoading workflows...")
    orchestrator.decomposer.es_service.create_index(delete_existing=True)
    orchestrator.decomposer.load_and_index_workflows("workflows.json")

    # Example 1: Estimate price and search
    print("\n" + "="*70)
    print("EXAMPLE: Agent queries marketplace")
    print("="*70)

    raw_query = "I need to file my Ohio 2024 taxes with W2 and itemized deductions"
    raw_context = {
        "name": "John Smith",  # PII - will be removed
        "ssn": "123-45-6789",  # PII - will be removed
        "exact_income": 87432.18,  # PII - will be bucketed
        "state": "ohio",
        "year": 2024
    }

    # Get estimate
    response = orchestrator.estimate_price_and_search(
        raw_query=raw_query,
        raw_context=raw_context,
        top_k=3
    )

    print("\n=== RESPONSE ===")
    import json
    print(json.dumps(response, indent=2))  # ✅ response is already a dict

    # Example 2: Buy solution
    print("\n" + "="*70)
    print("EXAMPLE: Agent purchases solution")
    print("="*70)

    # Extract session_id and pick first solution
    session_id = response["session_id"]
    solution_id = response["solutions"][0]["solution_id"]

    purchase = orchestrator.buy_solution(
        session_id=session_id,  # ✅ Correct signature
        solution_id=solution_id
    )

    print("\n=== PURCHASE RECEIPT ===")
    print(json.dumps(purchase, indent=2))
