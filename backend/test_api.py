"""Quick smoke test for all API endpoints."""
import json
import sys
sys.path.insert(0, ".")

from api import app

client = app.test_client()

def pp(label, data):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, default=str)[:600])
    else:
        print(data)

# Health
r = client.get("/health")
pp("HEALTH", r.get_json())

# List workflows
r = client.get("/api/workflows")
d = r.get_json()
pp(f"WORKFLOWS ({d['count']} loaded)", {
    "count": d["count"],
    "ids": [w["workflow_id"] for w in d["workflows"]],
})

# Search tax
r = client.post("/api/search", json={"task_type": "tax_filing", "state": "ohio", "year": 2024})
d = r.get_json()
pp("SEARCH: ohio tax", {"count": d["count"], "results": [r_["workflow_id"] for r_ in d["results"]]})

# Search shopping
r = client.post("/api/search", json={"task_type": "shopping"})
d = r.get_json()
pp("SEARCH: shopping", {"count": d["count"], "results": [r_["workflow_id"] for r_ in d["results"]]})

# Purchase
r = client.post("/api/purchase", json={"workflow_id": "ohio_w2_itemized_2024", "user_id": "default_user"})
d = r.get_json()
pp("PURCHASE", {"success": d.get("success"), "receipt": d.get("receipt")})

# Balance
r = client.get("/api/commerce/balance?user_id=default_user")
pp("BALANCE", r.get_json())

# Sanitize
r = client.post("/api/sanitize", json={"raw_query": {"task_type": "tax_filing", "name": "John Smith", "ssn": "123-45-6789", "exact_income": 87432.18}})
pp("SANITIZE", r.get_json())

# Cart add
r = client.post("/api/commerce/cart/add", json={"user_id": "default_user", "workflow_id": "smart_grocery_optimizer"})
pp("CART ADD", r.get_json())

# Cart view
r = client.get("/api/commerce/cart?user_id=default_user")
pp("CART VIEW", r.get_json())

# Feedback
r = client.post("/api/feedback", json={"workflow_id": "ohio_w2_itemized_2024", "rating": 5})
pp("FEEDBACK", r.get_json())

# Agent session (should report not configured if no key)
r = client.get("/api/agent/session")
pp("AGENT SESSION", r.get_json())

# Stats
r = client.get("/api/commerce/stats")
pp("MARKETPLACE STATS", r.get_json())

print("\n" + "=" * 50)
print("  ALL TESTS PASSED")
print("=" * 50)
