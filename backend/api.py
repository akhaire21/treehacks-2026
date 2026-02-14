"""
Flask API for Agent Workflow Marketplace.

Endpoints:
1. POST /api/estimate - Estimate pricing and search (no purchase)
2. POST /api/buy - Purchase solution and get execution plan
3. POST /api/feedback - Rate workflow (upvote/downvote)
4. GET /health - Health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import initialize_services
from orchestrator import MarketplaceOrchestrator

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global orchestrator instance
orchestrator = None


def init_app():
    """Initialize application and services."""
    global orchestrator

    print("="*70)
    print("Initializing Agent Workflow Marketplace API")
    print("="*70)

    # Initialize services
    try:
        initialize_services()
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Please create .env file with required API keys")
        sys.exit(1)

    # Create orchestrator
    orchestrator = MarketplaceOrchestrator()

    # Load and index workflows (one-time setup)
    print("\nLoading workflows into Elasticsearch...")
    try:
        orchestrator.decomposer.es_service.create_index(delete_existing=False)
    except Exception:
        print("  Index already exists")

    try:
        orchestrator.decomposer.load_and_index_workflows("workflows.json")
    except Exception as e:
        print(f"  Workflows already indexed: {e}")

    print("\n" + "="*70)
    print("✓ API Ready")
    print("="*70 + "\n")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Agent Workflow Marketplace",
        "version": "1.0.0"
    })


@app.route('/api/estimate', methods=['POST'])
def estimate_price_and_search():
    """
    Estimate pricing and search for solutions (no purchase).

    Request body:
    {
        "query": "Natural language query",
        "context": {
            "optional": "metadata",
            "may_contain": "PII"
        },
        "top_k": 5  // optional, default 5
    }

    Response:
    {
        "query": {
            "sanitized": {...},
            "privacy_protected": true
        },
        "decomposition": {
            "num_subtasks": 4,
            "subtasks": [
                {
                    "text": "Subtask description",
                    "task_type": "calculation|research|data_extraction",
                    "weight": 0.25,
                    "rationale": "Why this subtask is needed"
                }
            ]
        },
        "solutions": [
            {
                "solution_id": "sol_1",
                "rank": 1,
                "confidence_score": 0.92,
                "pricing": {
                    "total_cost_tokens": 1000,
                    "download_cost": 200,
                    "execution_cost": 800,
                    "from_scratch_estimate": 4000,
                    "savings_tokens": 3000,
                    "savings_percentage": 75
                },
                "structure": {
                    "num_workflows": 4,
                    "num_subtasks": 4,
                    "coverage": 1.0,
                    "execution_order": ["subtask_0", "subtask_1", ...]
                },
                "workflows_summary": [
                    {
                        "workflow_id": "ohio_w2_itemized_2024",
                        "workflow_title": "Ohio W2 + Itemized Deductions",
                        "task_type": "calculation",
                        "subtask_description": "Calculate Ohio state taxes",
                        "token_cost": 250
                    }
                ]
            }
        ],
        "num_solutions": 3,
        "session_id": "session_abc123"  // Use this for /api/buy
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request body"
            }), 400

        query = data['query']
        context = data.get('context', None)
        top_k = data.get('top_k', 5)

        # Call orchestrator
        response = orchestrator.estimate_price_and_search(
            raw_query=query,
            raw_context=context,
            top_k=top_k
        )

        # Return response (already a dict)
        return jsonify(response)

    except Exception as e:
        print(f"ERROR in /api/estimate: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": "internal_server_error"
        }), 500


@app.route('/api/buy', methods=['POST'])
def buy_solution():
    """
    Purchase solution and get execution plan.

    Request body:
    {
        "session_id": "session_abc123",  // From /api/estimate response
        "solution_id": "sol_1"           // Which solution to buy (sol_1, sol_2, etc.)
    }

    Response:
    {
        "purchase_id": "unique_purchase_id",
        "timestamp": "2024-02-14T12:00:00Z",
        "tokens_charged": 1000,
        "num_workflows": 4,
        "execution_plan": {
            "execution_order": [...],
            "root_ids": [...],
            "workflows": [
                {
                    "subtask_id": "subtask_0",
                    "description": "...",
                    "workflow_id": "...",
                    "workflow": {
                        // Full workflow with steps, edge_cases, domain_knowledge
                    },
                    "dependencies": [...],
                    "children": [...]
                }
            ]
        },
        "status": "purchased"
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'session_id' not in data or 'solution_id' not in data:
            return jsonify({
                "error": "Missing 'session_id' or 'solution_id' in request body"
            }), 400

        session_id = data['session_id']
        solution_id = data['solution_id']

        # Call orchestrator (it will retrieve cached solution)
        purchase = orchestrator.buy_solution(
            session_id=session_id,
            solution_id=solution_id
        )

        return jsonify(purchase)

    except Exception as e:
        print(f"ERROR in /api/buy: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": "internal_server_error"
        }), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback on a workflow (upvote/downvote).

    Request body:
    {
        "workflow_id": "ohio_w2_itemized_2024",
        "vote": "up" | "down",
        "comment": "Optional feedback comment"
    }

    Response:
    {
        "status": "success",
        "workflow_id": "ohio_w2_itemized_2024",
        "new_rating": 4.8,
        "new_usage_count": 48
    }
    """
    try:
        data = request.get_json()

        if not data or 'workflow_id' not in data or 'vote' not in data:
            return jsonify({
                "error": "Missing 'workflow_id' or 'vote' in request body"
            }), 400

        workflow_id = data['workflow_id']
        vote = data['vote']

        if vote not in ['up', 'down']:
            return jsonify({
                "error": "'vote' must be 'up' or 'down'"
            }), 400

        # In production, update Elasticsearch document
        # For now, just return mock response
        return jsonify({
            "status": "success",
            "workflow_id": workflow_id,
            "vote": vote,
            "message": "Feedback recorded"
        })

    except Exception as e:
        print(f"ERROR in /api/feedback: {e}")
        return jsonify({
            "error": str(e),
            "type": "internal_server_error"
        }), 500


@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """
    List all available workflows (for browsing).

    Query params:
    - task_type: Filter by task type
    - limit: Max results (default 20)

    Response:
    {
        "workflows": [
            {
                "workflow_id": "...",
                "title": "...",
                "task_type": "...",
                "rating": 4.8,
                "usage_count": 47,
                "token_cost": 200
            }
        ],
        "total": 8
    }
    """
    try:
        task_type = request.args.get('task_type')
        limit = int(request.args.get('limit', 20))

        # Query Elasticsearch for workflows
        query = {"match_all": {}}

        if task_type:
            query = {
                "bool": {
                    "must": [
                        {"term": {"node_type": "workflow"}},
                        {"term": {"task_type": task_type}}
                    ]
                }
            }
        else:
            query = {"term": {"node_type": "workflow"}}

        results = orchestrator.decomposer.es_service.es.search(
            index=orchestrator.decomposer.es_service.index_name,
            body={"query": query, "size": limit}
        )

        workflows = []
        for hit in results['hits']['hits']:
            workflow = hit['_source']
            workflows.append({
                "workflow_id": workflow['workflow_id'],
                "title": workflow['title'],
                "task_type": workflow['task_type'],
                "description": workflow.get('description', ''),
                "rating": workflow.get('rating', 0),
                "usage_count": workflow.get('usage_count', 0),
                "token_cost": workflow.get('token_cost', 200),
                "execution_tokens": workflow.get('execution_tokens', 800),
                "tags": workflow.get('tags', [])
            })

        return jsonify({
            "workflows": workflows,
            "total": len(workflows)
        })

    except Exception as e:
        print(f"ERROR in /api/workflows: {e}")
        return jsonify({
            "error": str(e),
            "type": "internal_server_error"
        }), 500


@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """Get all available workflows (for browsing)."""
    return jsonify({
        'workflows': matcher.workflows,
        'count': len(matcher.workflows)
    })


@app.route('/api/pricing/<workflow_id>', methods=['GET'])
def get_workflow_pricing(workflow_id):
    """
    Get detailed pricing breakdown for a specific workflow.

    Response:
    {
        "workflow_id": "ohio_w2_itemized_2024",
        "title": "...",
        "price_tokens": 200,
        "tokens_saved": 11800,
        "savings_percentage": 69,
        "roi_percentage": 5900,
        "pricing": {
            "base_price": 1770,
            "quality_multiplier": 1.08,
            "market_rate": 185,
            "breakdown": "Base: 1770 (15% of 11800 saved) → Quality adjusted (4.8★): ×1.08 → Final: 200 tokens"
        },
        "avg_tokens_without": 15000,
        "avg_tokens_with": 3200
    }
    """
    try:
        workflow = matcher.get_workflow_by_id(workflow_id)

        if not workflow:
            return jsonify({
                'error': 'Workflow not found'
            }), 404

        pricing_info = {
            'workflow_id': workflow['workflow_id'],
            'title': workflow['title'],
            'price_tokens': workflow.get('price_tokens', 0),
            'tokens_saved': workflow.get('tokens_saved', 0),
            'savings_percentage': workflow.get('savings_percentage', 0),
            'roi_percentage': workflow.get('pricing', {}).get('roi_percentage', 0),
            'pricing': workflow.get('pricing', {}),
            'avg_tokens_without': workflow.get('avg_tokens_without', 0),
            'avg_tokens_with': workflow.get('avg_tokens_with', 0),
            'rating': workflow.get('rating', 0),
            'usage_count': workflow.get('usage_count', 0)
        }

        return jsonify(pricing_info)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Initialize app
    init_app()

    # Run server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
