"""Quick test: try the values in swapped positions and also try as URL."""
import os, base64
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
api_key = os.getenv("ELASTIC_API_KEY", "")

print(f"ELASTIC_CLOUD_ID = {cloud_id}")
print(f"ELASTIC_API_KEY  = {api_key[:30]}...")
print()

# Try to decode cloud_id as base64
for label, val in [("CLOUD_ID", cloud_id), ("API_KEY", api_key)]:
    try:
        decoded = base64.b64decode(val + "==").decode("utf-8", errors="replace")
        print(f"{label} base64 decode: {decoded[:100]}")
    except Exception as e:
        print(f"{label} base64 decode failed: {e}")

print()

# Try connecting with swapped values
from elasticsearch import Elasticsearch

# Attempt 1: Original
print("Attempt 1: Original values...")
try:
    es = Elasticsearch(cloud_id=cloud_id, api_key=api_key)
    info = es.info()
    print(f"  SUCCESS: {info['cluster_name']} v{info['version']['number']}")
except Exception as e:
    print(f"  FAILED: {e}")

# Attempt 2: Just API key with common Elastic Cloud URL pattern
print("\nAttempt 2: Try as API key auth against cloud_id...")
try:
    # The cloud_id might be the deployment ID, try constructing URL
    es = Elasticsearch(
        cloud_id=api_key,
        api_key=cloud_id,
    )
    info = es.info()
    print(f"  SUCCESS: {info['cluster_name']} v{info['version']['number']}")
except Exception as e:
    print(f"  FAILED: {e}")
