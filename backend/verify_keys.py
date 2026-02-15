"""
Verify all API keys and services are working.
Tests: JINA Embeddings, Elasticsearch Cloud, Anthropic Claude
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def ok(msg):
    print(f"  {GREEN}✓{RESET} {msg}")

def fail(msg):
    print(f"  {RED}✗{RESET} {msg}")

def warn(msg):
    print(f"  {YELLOW}⚠{RESET} {msg}")

all_pass = True

# ─────────────────────────────────────────────────────────
# 1. JINA Embeddings
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}[1/3] JINA Embeddings API{RESET}")
jina_key = os.getenv("JINA_API_KEY", "")
if not jina_key:
    fail("JINA_API_KEY not set")
    all_pass = False
else:
    try:
        import requests
        resp = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {jina_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "jina-embeddings-v3",
                "input": ["test embedding for verification"],
                "task": "retrieval.passage",
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            dim = len(data["data"][0]["embedding"])
            ok(f"JINA API working — model=jina-embeddings-v3, dims={dim}")
            ok(f"Embedding sample (first 5 values): {data['data'][0]['embedding'][:5]}")
        else:
            fail(f"JINA API returned {resp.status_code}: {resp.text[:200]}")
            all_pass = False
    except Exception as e:
        fail(f"JINA API error: {e}")
        all_pass = False

# ─────────────────────────────────────────────────────────
# 2. Elasticsearch Cloud
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}[2/3] Elasticsearch Cloud{RESET}")
cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
elastic_key = os.getenv("ELASTIC_API_KEY", "")
if not cloud_id or not elastic_key:
    fail("ELASTIC_CLOUD_ID or ELASTIC_API_KEY not set")
    all_pass = False
else:
    try:
        from elastic_client import ElasticClient, JinaEmbedder
        embedder = JinaEmbedder(api_key=os.getenv("JINA_API_KEY", ""))
        ec = ElasticClient(cloud_id=cloud_id, api_key=elastic_key, jina_embedder=embedder)
        info = ec.es.info()
        ok(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
        ok(f"Version: {info['version']['number']}")

        # Check if index exists
        index_name = os.getenv("ELASTIC_INDEX", "workflows")
        if ec.es.indices.exists(index=index_name):
            count = ec.es.count(index=index_name)["count"]
            ok(f"Index '{index_name}' exists with {count} documents")
        else:
            warn(f"Index '{index_name}' does not exist yet — run setup_elastic.py to create it")
    except Exception as e:
        fail(f"Elasticsearch error: {e}")
        all_pass = False

# ─────────────────────────────────────────────────────────
# 3. Anthropic Claude
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}[3/3] Anthropic Claude API{RESET}")
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
if not anthropic_key:
    fail("ANTHROPIC_API_KEY not set")
    all_pass = False
else:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Reply with only: VERIFIED"}],
        )
        text = resp.content[0].text.strip()
        ok(f"Claude API working — model={resp.model}")
        ok(f"Response: {text}")
        ok(f"Usage: input={resp.usage.input_tokens} output={resp.usage.output_tokens} tokens")
    except Exception as e:
        fail(f"Claude API error: {e}")
        all_pass = False

# ─────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────
print(f"\n{'='*50}")
if all_pass:
    print(f"  {GREEN}{BOLD}ALL SERVICES VERIFIED ✓{RESET}")
else:
    print(f"  {RED}{BOLD}SOME SERVICES FAILED — check above{RESET}")
print(f"{'='*50}\n")

sys.exit(0 if all_pass else 1)
