"""
Main Flask API for Agent Workflow Marketplace.
Provides search, purchase, and rating endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from matcher import WorkflowMatcher
from sanitizer import PrivacySanitizer
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize services
matcher = WorkflowMatcher()
sanitizer = PrivacySanitizer()

# Load workflows on startup
WORKFLOWS_PATH = os.path.join(os.path.dirname(__file__), 'workflows.json')
matcher.load_workflows(WORKFLOWS_PATH)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'workflows_loaded': len(matcher.workflows)
    })


@app.route('/api/search', methods=['POST'])
def search_workflows():
    """
    Search for matching workflows.

    Request body:
    {
        "task_type": "tax_filing",
        "state": "ohio",
        "year": 2024,
        "income_bracket": "80k-100k",  // Already bucketed by client
        "deduction_type": "itemized",
        "filing_status": "married_jointly"
    }

    Response:
    {
        "results": [
            {
                "workflow_id": "ohio_w2_itemized_2024",
                "title": "Ohio 2024 IT-1040 (W2, Itemized, Married)",
                "description": "...",
                "token_cost": 200,
                "rating": 4.8,
                "usage_count": 47,
                "similarity_score": 0.93,
                "match_percentage": 93
            },
            ...
        ],
        "count": 3
    }
    """
    try:
        query = request.json

        if not query or 'task_type' not in query:
            return jsonify({
                'error': 'Missing required field: task_type'
            }), 400

        # Search workflows
        results = matcher.search(query, top_k=10)

        return jsonify({
            'results': results,
            'count': len(results),
            'query': query
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/purchase', methods=['POST'])
def purchase_workflow():
    """
    Purchase a workflow and return execution template.

    Request body:
    {
        "workflow_id": "ohio_w2_itemized_2024"
    }

    Response:
    {
        "workflow": {
            "workflow_id": "ohio_w2_itemized_2024",
            "title": "...",
            "steps": [...],  // Full workflow with placeholders
            "token_cost": 200,
            "purchased_at": "2024-02-14T10:30:00"
        },
        "success": true
    }
    """
    try:
        data = request.json

        if not data or 'workflow_id' not in data:
            return jsonify({
                'error': 'Missing required field: workflow_id'
            }), 400

        workflow_id = data['workflow_id']
        workflow = matcher.get_workflow_by_id(workflow_id)

        if not workflow:
            return jsonify({
                'error': 'Workflow not found'
            }), 404

        # Increment usage count (in real app, would persist to DB)
        workflow['usage_count'] = workflow.get('usage_count', 0) + 1

        # Return full workflow with execution details
        return jsonify({
            'workflow': workflow,
            'purchased_at': datetime.now().isoformat(),
            'success': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/feedback', methods=['POST'])
def rate_workflow():
    """
    Rate a workflow (upvote/downvote or star rating).

    Request body:
    {
        "workflow_id": "ohio_w2_itemized_2024",
        "rating": 5,  // 1-5 stars, or
        "vote": "up"  // "up" or "down"
    }

    Response:
    {
        "workflow_id": "ohio_w2_itemized_2024",
        "new_rating": 4.9,
        "new_usage_count": 48,
        "success": true
    }
    """
    try:
        data = request.json

        if not data or 'workflow_id' not in data:
            return jsonify({
                'error': 'Missing required field: workflow_id'
            }), 400

        workflow_id = data['workflow_id']
        workflow = matcher.get_workflow_by_id(workflow_id)

        if not workflow:
            return jsonify({
                'error': 'Workflow not found'
            }), 404

        # Update rating (simplified - in real app would track all ratings)
        if 'rating' in data:
            new_rating_value = data['rating']
            current_rating = workflow.get('rating', 5.0)
            # Simple averaging (would be more sophisticated in production)
            workflow['rating'] = round((current_rating + new_rating_value) / 2, 1)

        elif 'vote' in data:
            vote = data['vote']
            if vote == 'up':
                workflow['rating'] = min(5.0, workflow.get('rating', 5.0) + 0.1)
            elif vote == 'down':
                workflow['rating'] = max(1.0, workflow.get('rating', 5.0) - 0.1)

        return jsonify({
            'workflow_id': workflow_id,
            'new_rating': workflow['rating'],
            'new_usage_count': workflow.get('usage_count', 0),
            'success': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/sanitize', methods=['POST'])
def sanitize_query():
    """
    Demonstrate privacy sanitization (for UI demo).

    Request body:
    {
        "raw_query": {
            "task_type": "tax_filing",
            "name": "John Smith",
            "ssn": "123-45-6789",
            "exact_income": 87432.18
        }
    }

    Response:
    {
        "public_query": {...},  // Sanitized
        "private_data": {...},  // What stays local
        "sanitization_summary": {...}
    }
    """
    try:
        data = request.json

        if not data or 'raw_query' not in data:
            return jsonify({
                'error': 'Missing required field: raw_query'
            }), 400

        raw_query = data['raw_query']
        public_query, private_data = sanitizer.sanitize_query(raw_query)
        summary = sanitizer.get_sanitization_summary(raw_query, public_query)

        return jsonify({
            'public_query': public_query,
            'private_data': private_data,
            'sanitization_summary': summary
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """Get all available workflows (for browsing)."""
    return jsonify({
        'workflows': matcher.workflows,
        'count': len(matcher.workflows)
    })


if __name__ == '__main__':
    print("🚀 Agent Workflow Marketplace API starting...")
    print(f"📦 Loaded {len(matcher.workflows)} workflows")
    print("🔗 API available at http://localhost:5001")
    print("\nEndpoints:")
    print("  POST /api/search     - Search workflows")
    print("  POST /api/purchase   - Purchase workflow")
    print("  POST /api/feedback   - Rate workflow")
    print("  POST /api/sanitize   - Demo privacy sanitization")
    print("  GET  /api/workflows  - List all workflows")
    print("  GET  /health         - Health check")

    app.run(debug=True, host='0.0.0.0', port=5001)
