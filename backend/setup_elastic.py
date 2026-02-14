"""
Elasticsearch Index Setup & Workflow Ingestion Script.

Run once to:
  1. Create the 'workflows' index with dense_vector mapping
  2. Generate JINA embeddings for all workflows
  3. Bulk-index everything into Elastic Cloud

Usage:
    python setup_elastic.py

Requires ELASTIC_CLOUD_ID, ELASTIC_API_KEY, and JINA_API_KEY in .env
"""

import os
import json
import sys
from dotenv import load_dotenv

# Load env from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from elastic_client import ElasticClient, JinaEmbedder


def main():
    print("=" * 60)
    print("  Agent Workflow Marketplace — Elastic Setup")
    print("=" * 60)

    # Check required env vars
    cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
    api_key = os.getenv("ELASTIC_API_KEY", "")
    jina_key = os.getenv("JINA_API_KEY", "")

    if not cloud_id or not api_key:
        print("\n[ERROR] ELASTIC_CLOUD_ID and ELASTIC_API_KEY must be set in .env")
        print("  1. Go to https://cloud.elastic.co and create a deployment")
        print("  2. Copy the Cloud ID and create an API key")
        print("  3. Add them to backend/.env")
        sys.exit(1)

    if not jina_key:
        print("\n[ERROR] JINA_API_KEY must be set in .env")
        print("  1. Go to https://jina.ai and get an API key")
        print("  2. Add it to backend/.env")
        sys.exit(1)

    # Load workflows from JSON
    workflows_path = os.path.join(os.path.dirname(__file__), "workflows.json")
    with open(workflows_path, "r") as f:
        data = json.load(f)
    workflows = data["workflows"]
    print(f"\n[1/3] Loaded {len(workflows)} workflows from workflows.json")

    # Initialize clients
    embedder = JinaEmbedder(api_key=jina_key)
    elastic = ElasticClient(cloud_id=cloud_id, api_key=api_key, jina_embedder=embedder)

    # Create index (deletes existing if present)
    print("\n[2/3] Creating Elasticsearch index with dense_vector mapping …")
    elastic.create_index()

    # Ingest workflows with JINA embeddings
    print("\n[3/3] Embedding workflows with JINA and indexing into Elasticsearch …")
    elastic.ingest_workflows(workflows)

    # Verify
    count = elastic.count()
    print(f"\n{'='*60}")
    print(f"  Setup complete! {count} workflows indexed.")
    print(f"  Index: {elastic.index_name}")
    print(f"  Elastic Cloud: {cloud_id[:30]}…")
    print(f"{'='*60}")

    # Quick test
    print("\n[test] Running test hybrid search: 'ohio tax filing' …")
    results = elastic.hybrid_search("ohio tax filing", filters={"task_type": "tax_filing"}, top_k=3)
    for r in results:
        print(f"  → {r['workflow_id']} | score={r.get('_score', 'n/a')} | {r['title']}")

    print("\nDone! Start the API with: python api.py")


if __name__ == "__main__":
    main()
