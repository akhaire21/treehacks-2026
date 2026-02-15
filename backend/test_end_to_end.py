"""
End-to-end test for the workflow marketplace system.

Tests the complete flow:
1. Create indices
2. Load workflows
3. Decompose query
4. Search workflows
5. Compose execution plan
"""

import sys
from config import initialize_services
from query_decomposer import RecursiveQueryDecomposer


def main():
    print("=" * 80)
    print("WORKFLOW MARKETPLACE - END-TO-END TEST")
    print("=" * 80)

    # Step 1: Initialize all services
    print("\n[Step 1/5] Initializing services...")
    try:
        services = initialize_services()
        print("✓ All services initialized")
    except Exception as e:
        print(f"✗ Failed to initialize services: {e}")
        return False

    es_service = services['elasticsearch_service']
    decomposer = RecursiveQueryDecomposer()

    # Step 2: Create indices
    print("\n[Step 2/5] Creating Elasticsearch indices...")
    try:
        # Check if indices already exist
        existing = es_service.es.indices.exists(index=es_service.index_name)
        if existing:
            print(f"  ℹ Assets index '{es_service.index_name}' already exists")
            recreate = input("  Recreate indices? (y/N): ").strip().lower()
            if recreate == 'y':
                es_service.create_index(delete_existing=True)
                es_service.create_nodes_index(delete_existing=True)
                print("  ✓ Indices recreated")
            else:
                print("  ✓ Using existing indices")
        else:
            es_service.create_index()
            es_service.create_nodes_index()
            print("  ✓ Indices created")
    except Exception as e:
        print(f"  ✗ Failed to create indices: {e}")
        return False

    # Step 3: Load workflows
    print("\n[Step 3/5] Loading and indexing workflows...")
    try:
        # Check if workflows already indexed
        count_response = es_service.es.count(index=es_service.index_name)
        doc_count = count_response.get('count', 0)

        if doc_count > 0:
            print(f"  ℹ Found {doc_count} existing workflows in index")
            reindex = input("  Reindex workflows? (y/N): ").strip().lower()
            if reindex != 'y':
                print("  ✓ Using existing workflows")
            else:
                decomposer.load_and_index_workflows("workflows.json")
        else:
            decomposer.load_and_index_workflows("workflows.json")

        # Verify indexing
        count_response = es_service.es.count(index=es_service.index_name)
        workflow_count = count_response.get('count', 0)

        nodes_count_response = es_service.es.count(index=es_service.nodes_index_name)
        nodes_count = nodes_count_response.get('count', 0)

        print(f"  ✓ Indexed: {workflow_count} workflows, {nodes_count} nodes")

        if workflow_count == 0:
            print("  ✗ No workflows indexed!")
            return False

    except Exception as e:
        print(f"  ✗ Failed to load workflows: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Test query decomposition and search
    print("\n[Step 4/5] Testing query decomposition and search...")

    # Example queries to test
    test_queries = [
        "I need to file my Ohio 2024 taxes with W2 income",
        "Plan a family trip to Tokyo with kids",
        "Help me parse a Stripe invoice"
    ]

    print("\nAvailable test queries:")
    for i, q in enumerate(test_queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(test_queries) + 1}. Custom query")

    choice = input(f"\nSelect query (1-{len(test_queries) + 1}): ").strip()

    if choice == str(len(test_queries) + 1):
        query = input("Enter custom query: ").strip()
    else:
        try:
            idx = int(choice) - 1
            query = test_queries[idx]
        except (ValueError, IndexError):
            query = test_queries[0]

    print(f"\n{'=' * 80}")
    print(f"QUERY: {query}")
    print(f"{'=' * 80}")

    try:
        # Run search with decomposition
        search_plan = decomposer.search(query, top_k=5)

        # Step 5: Display results
        print(f"\n{'=' * 80}")
        print("SEARCH RESULTS")
        print(f"{'=' * 80}")

        print(f"\nPlan Type: {search_plan.plan_type.upper()}")
        print(f"Overall Score: {search_plan.overall_score:.3f}")
        print(f"Workflows Found: {len(search_plan.workflows)}")

        if search_plan.is_composite:
            print(f"Coverage: {search_plan.coverage}")
            print(f"\n--- COMPOSITE PLAN ---")
            print(f"Subtasks: {len(search_plan.subtasks)}")

            for i, subtask in enumerate(search_plan.subtasks):
                print(f"\n  Subtask {i+1}: {subtask.text}")
                print(f"    Type: {subtask.task_type}")
                print(f"    Weight: {subtask.weight}")

                if i in search_plan.subtask_workflow_mapping:
                    wf_idx = search_plan.subtask_workflow_mapping[i]
                    workflow = search_plan.workflows[wf_idx]
                    print(f"    → Matched to: {workflow.title}")
                    print(f"       Cost: {workflow.total_cost} tokens")
                    print(f"       Score: {workflow.similarity_score:.3f}")

        else:
            print(f"\n--- DIRECT MATCH POOL ---")

        print(f"\n--- ALL WORKFLOWS ---")
        for i, workflow in enumerate(search_plan.workflows[:10], 1):
            print(f"\n{i}. {workflow.title}")
            print(f"   ID: {workflow.workflow_id}")
            print(f"   Type: {workflow.task_type}")
            print(f"   Download: {workflow.download_cost} tokens")
            print(f"   Execution: {workflow.execution_cost} tokens")
            print(f"   Total: {workflow.total_cost} tokens")
            print(f"   Rating: {workflow.rating}/5.0")
            print(f"   Score: {workflow.similarity_score:.3f}")

        print(f"\n{'=' * 80}")
        print("✓ END-TO-END TEST COMPLETE!")
        print(f"{'=' * 80}")

        return True

    except Exception as e:
        print(f"\n✗ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
