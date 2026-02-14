"""
Main Flask API for the Agent Workflow Marketplace.

Endpoints:
  ── Core Marketplace ──
  GET  /health                   Health check
  GET  /api/workflows            List all workflows
  POST /api/search               Hybrid search (Elastic kNN + BM25)
  POST /api/purchase             Purchase a workflow
  POST /api/feedback             Rate a workflow

  ── Privacy ──
  POST /api/sanitize             Demo PII sanitization

  ── Claude Agent ──
  POST /api/agent/chat           Multi-turn agent conversation
  GET  /api/agent/session        Get session state
  POST /api/agent/reset          Reset agent session

  ── Commerce ──
  GET  /api/commerce/balance     Get user balance
  POST /api/commerce/deposit     Add credits
  POST /api/commerce/cart/add    Add workflow to cart
  POST /api/commerce/cart/remove Remove from cart
  GET  /api/commerce/cart        View cart
  POST /api/commerce/checkout    Checkout cart
  GET  /api/commerce/transactions Transaction history
  GET  /api/commerce/stats       Marketplace statistics

Tech stack: Flask, Elasticsearch, JINA embeddings, Claude Agent SDK
"""

import os
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from sanitizer import PrivacySanitizer
from commerce import CommerceEngine

# ---------------------------------------------------------------------------
# Try to initialize Elasticsearch + JINA (graceful fallback if keys missing)
# ---------------------------------------------------------------------------
elastic_client = None
try:
    cloud_id = os.getenv("ELASTIC_CLOUD_ID", "")
    api_key = os.getenv("ELASTIC_API_KEY", "")
    jina_key = os.getenv("JINA_API_KEY", "")

    if cloud_id and api_key and jina_key:
        from elastic_client import ElasticClient, JinaEmbedder

        embedder = JinaEmbedder(api_key=jina_key)
        elastic_client = ElasticClient(
            cloud_id=cloud_id, api_key=api_key, jina_embedder=embedder
        )
        print("[api] Elasticsearch + JINA connected")
    else:
        print("[api] Elastic/JINA keys not set — running in-memory fallback mode")
except Exception as e:
    print(f"[api] Elasticsearch init failed ({e}) — using in-memory fallback")

# ---------------------------------------------------------------------------
# Initialize services
# ---------------------------------------------------------------------------
from matcher import WorkflowMatcher

matcher = WorkflowMatcher(elastic_client=elastic_client)
sanitizer = PrivacySanitizer()
commerce = CommerceEngine()

# Load workflows from disk (always, for fallback + listing)
WORKFLOWS_PATH = os.path.join(os.path.dirname(__file__), "workflows.json")
matcher.load_workflows(WORKFLOWS_PATH)

# ---------------------------------------------------------------------------
# Initialize Claude Agent
# ---------------------------------------------------------------------------
agent_instance = None
try:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        from agent import MarketplaceAgent

        agent_instance = MarketplaceAgent(
            elastic_client=elastic_client,
            sanitizer=sanitizer,
            anthropic_api_key=anthropic_key,
        )
        print("[api] Claude Agent initialized")
    else:
        print("[api] ANTHROPIC_API_KEY not set — agent endpoints disabled")
except Exception as e:
    print(f"[api] Agent init failed ({e}) — agent endpoints disabled")

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)


# ===== HEALTH =====

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "workflows_loaded": len(matcher.workflows),
        "elasticsearch": elastic_client is not None,
        "agent_enabled": agent_instance is not None,
    })


# ===== CORE MARKETPLACE =====

@app.route("/api/workflows", methods=["GET"])
def list_workflows():
    workflows = matcher.get_all_workflows()
    return jsonify({"workflows": workflows, "count": len(workflows)})


@app.route("/api/search", methods=["POST"])
def search_workflows():
    """
    Hybrid search: Elasticsearch kNN (JINA vectors) + BM25.
    Falls back to in-memory if Elastic not configured.

    Body: { "task_type": "...", "state": "...", ... }
    """
    try:
        query = request.json
        if not query:
            return jsonify({"error": "Request body required"}), 400

        results = matcher.search(query, top_k=10)
        return jsonify({"results": results, "count": len(results), "query": query})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/purchase", methods=["POST"])
def purchase_workflow():
    """Purchase a workflow. Deducts tokens, returns full execution template."""
    try:
        data = request.json or {}
        workflow_id = data.get("workflow_id")
        user_id = data.get("user_id", "default_user")

        if not workflow_id:
            return jsonify({"error": "Missing workflow_id"}), 400

        workflow = matcher.get_workflow_by_id(workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404

        # Process purchase through commerce engine
        receipt = commerce.purchase_workflow(user_id, workflow)
        if not receipt["success"]:
            return jsonify(receipt), 402  # Payment Required

        return jsonify({
            "workflow": workflow,
            "receipt": receipt,
            "purchased_at": datetime.now().isoformat(),
            "success": True,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def rate_workflow():
    """Rate a workflow (1-5 stars or up/down vote)."""
    try:
        data = request.json or {}
        workflow_id = data.get("workflow_id")
        if not workflow_id:
            return jsonify({"error": "Missing workflow_id"}), 400

        workflow = matcher.get_workflow_by_id(workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404

        if "rating" in data:
            new_val = data["rating"]
            old = workflow.get("rating", 5.0)
            workflow["rating"] = round((old + new_val) / 2, 1)
        elif "vote" in data:
            if data["vote"] == "up":
                workflow["rating"] = min(5.0, workflow.get("rating", 5.0) + 0.1)
            elif data["vote"] == "down":
                workflow["rating"] = max(1.0, workflow.get("rating", 5.0) - 0.1)

        # Persist to Elastic if available
        if elastic_client:
            try:
                elastic_client.update_field(workflow_id, "rating", workflow["rating"])
            except Exception:
                pass

        return jsonify({
            "workflow_id": workflow_id,
            "new_rating": workflow["rating"],
            "new_usage_count": workflow.get("usage_count", 0),
            "success": True,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== PRIVACY =====

@app.route("/api/sanitize", methods=["POST"])
def sanitize_query():
    """Demonstrate the two-layer privacy architecture."""
    try:
        data = request.json or {}
        raw_query = data.get("raw_query", {})
        if not raw_query:
            return jsonify({"error": "Missing raw_query"}), 400

        public_query, private_data = sanitizer.sanitize_query(raw_query)
        summary = sanitizer.get_sanitization_summary(raw_query, public_query)

        return jsonify({
            "public_query": public_query,
            "private_data": private_data,
            "sanitization_summary": summary,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== CLAUDE AGENT =====

@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    """
    Multi-turn conversation with the Claude-powered agent.
    The agent autonomously searches, evaluates, purchases, and executes workflows.

    Body: { "message": "Help me file my Ohio taxes" }
    """
    if not agent_instance:
        return jsonify({
            "error": "Agent not configured. Set ANTHROPIC_API_KEY in .env",
        }), 503

    try:
        data = request.json or {}
        message = data.get("message", "")
        if not message:
            return jsonify({"error": "Missing message"}), 400

        result = agent_instance.chat(message)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/session", methods=["GET"])
def agent_session():
    """Get current agent session state."""
    if not agent_instance:
        return jsonify({"error": "Agent not configured"}), 503
    return jsonify(agent_instance.get_session_summary())


@app.route("/api/agent/reset", methods=["POST"])
def agent_reset():
    """Reset the agent session (new conversation)."""
    if not agent_instance:
        return jsonify({"error": "Agent not configured"}), 503
    agent_instance.reset_session()
    return jsonify({"success": True, "message": "Session reset"})


# ===== COMMERCE =====

@app.route("/api/commerce/balance", methods=["GET"])
def get_balance():
    user_id = request.args.get("user_id", "default_user")
    return jsonify({"user_id": user_id, "balance": commerce.get_balance(user_id)})


@app.route("/api/commerce/deposit", methods=["POST"])
def deposit_credits():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    amount = data.get("amount", 0)
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    return jsonify(commerce.deposit(user_id, amount))


@app.route("/api/commerce/cart", methods=["GET"])
def view_cart():
    user_id = request.args.get("user_id", "default_user")
    cart = commerce.get_cart(user_id)
    return jsonify(cart.to_dict())


@app.route("/api/commerce/cart/add", methods=["POST"])
def add_to_cart():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    workflow_id = data.get("workflow_id")
    if not workflow_id:
        return jsonify({"error": "Missing workflow_id"}), 400

    workflow = matcher.get_workflow_by_id(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    return jsonify(commerce.add_to_cart(user_id, workflow))


@app.route("/api/commerce/cart/remove", methods=["POST"])
def remove_from_cart():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    workflow_id = data.get("workflow_id")
    if not workflow_id:
        return jsonify({"error": "Missing workflow_id"}), 400
    return jsonify(commerce.remove_from_cart(user_id, workflow_id))


@app.route("/api/commerce/checkout", methods=["POST"])
def checkout():
    """Checkout all items in the shopping cart."""
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    return jsonify(commerce.checkout_cart(user_id))


@app.route("/api/commerce/transactions", methods=["GET"])
def get_transactions():
    user_id = request.args.get("user_id")
    limit = int(request.args.get("limit", 50))
    return jsonify({
        "transactions": commerce.get_transactions(user_id, limit),
    })


@app.route("/api/commerce/stats", methods=["GET"])
def marketplace_stats():
    return jsonify(commerce.get_marketplace_stats())


# ===== START =====

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    print()
    print("=" * 60)
    print("  Agent Workflow Marketplace API")
    print("=" * 60)
    print(f"  Workflows loaded : {len(matcher.workflows)}")
    print(f"  Elasticsearch    : {'connected' if elastic_client else 'off (in-memory fallback)'}")
    print(f"  Claude Agent     : {'ready' if agent_instance else 'disabled (no API key)'}")
    print(f"  JINA Embeddings  : {'active' if elastic_client else 'off'}")
    print(f"  Commerce Engine  : active")
    print(f"  Server           : http://localhost:{port}")
    print()
    print("  Endpoints:")
    print("    POST /api/search          Search workflows (hybrid kNN + BM25)")
    print("    POST /api/purchase        Purchase workflow")
    print("    POST /api/feedback        Rate workflow")
    print("    POST /api/sanitize        Privacy sanitization demo")
    print("    POST /api/agent/chat      Claude multi-turn agent")
    print("    GET  /api/agent/session   Agent session state")
    print("    POST /api/agent/reset     Reset agent")
    print("    GET  /api/commerce/*      Commerce endpoints")
    print("    GET  /api/workflows       List all workflows")
    print("    GET  /health              Health check")
    print("=" * 60)

    app.run(debug=debug, host="0.0.0.0", port=port)
