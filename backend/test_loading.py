"""Test workflow loading and indexing."""
import sys
from config import initialize_services
from query_decomposer import RecursiveQueryDecomposer

def test_loading():
    print("="*70)
    print("TEST 1: Loading and Indexing Workflows")
    print("="*70)

    # Initialize services
    print("\n[1/4] Initializing services...")
    try:
        initialize_services()
        print("✓ Services initialized")
    except Exception as e:
        print(f"✗ Failed to initialize services: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Create decomposer
    print("\n[2/4] Creating decomposer...")
    decomposer = RecursiveQueryDecomposer()

    # Create index
    print("\n[3/4] Creating Elasticsearch index...")
    try:
        decomposer.es_service.create_index(delete_existing=True)
        print("✓ Index created")
    except Exception as e:
        print(f"✗ Failed to create index: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Load and index workflows
    print("\n[4/4] Loading workflows from JSON...")
    try:
        decomposer.load_and_index_workflows("workflows.json")
        print("\n" + "="*70)
        print("✓ SUCCESS: Workflows loaded and indexed!")
        print("="*70)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_loading()
