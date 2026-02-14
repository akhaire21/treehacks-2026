"""
Test script to verify Elasticsearch connection.

Run this to check if your Elastic Cloud or self-hosted ES is properly configured.
"""

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# Load environment variables
load_dotenv()

def test_connection():
    """Test Elasticsearch connection with current config."""

    print("=" * 60)
    print("Testing Elasticsearch Connection")
    print("=" * 60)

    # Get config from environment
    cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
    api_key = os.getenv("ELASTIC_API_KEY", "")
    host = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    username = os.getenv("ELASTICSEARCH_USERNAME", "")
    password = os.getenv("ELASTICSEARCH_PASSWORD", "")

    print("\nConfiguration detected:")
    if cloud_id:
        print(f"  Mode: Elastic Cloud")
        print(f"  Cloud ID: {cloud_id[:20]}...")
        print(f"  API Key: {'✓ Set' if api_key else '✗ Missing'}")
    elif host:
        print(f"  Mode: Self-Hosted")
        print(f"  Host: {host}")
        print(f"  Auth: {'Basic Auth' if username and password else 'None'}")
    else:
        print("  ✗ ERROR: No connection config found!")
        print("  Please set ELASTIC_CLOUD_ID or ELASTICSEARCH_HOST in .env")
        return False

    # Try to connect
    print("\nAttempting connection...")

    try:
        # Build connection
        if cloud_id and api_key:
            es = Elasticsearch(cloud_id=cloud_id, api_key=api_key)
        elif host:
            if username and password:
                es = Elasticsearch(hosts=[host], basic_auth=(username, password))
            else:
                es = Elasticsearch(hosts=[host])
        else:
            print("✗ Failed: No valid connection parameters")
            return False

        # Test ping
        if not es.ping():
            print("✗ Failed: Could not ping Elasticsearch")
            return False

        print("✓ Connection successful!")

        # Get cluster info
        info = es.info()
        print("\nCluster Information:")
        print(f"  Cluster Name: {info['cluster_name']}")
        print(f"  ES Version: {info['version']['number']}")
        print(f"  Lucene Version: {info['version']['lucene_version']}")

        # Get cluster health
        health = es.cluster.health()
        print(f"\nCluster Health:")
        print(f"  Status: {health['status']}")
        print(f"  Number of Nodes: {health['number_of_nodes']}")
        print(f"  Active Shards: {health['active_shards']}")

        # List indices
        indices = es.cat.indices(format="json")
        print(f"\nExisting Indices: {len(indices)}")
        if indices:
            for idx in indices[:5]:  # Show first 5
                print(f"  - {idx['index']} ({idx['docs.count']} docs, {idx['store.size']})")
            if len(indices) > 5:
                print(f"  ... and {len(indices) - 5} more")

        print("\n" + "=" * 60)
        print("✓ All checks passed! Elasticsearch is ready.")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Connection failed!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check your .env file has the correct credentials")
        print("  2. Verify your Cloud ID or host URL is correct")
        print("  3. For Cloud: Make sure API key has proper permissions")
        print("  4. For self-hosted: Check if ES is running (curl http://localhost:9200)")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
