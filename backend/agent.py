"""
Autonomous Claude Agent for the Workflow Marketplace.

Uses Anthropic tool_use to build a multi-turn agent that:
  1. Understands user tasks
  2. Searches the marketplace for matching workflows
  3. Evaluates, selects, and purchases workflows
  4. Executes workflow steps with user's private data
  5. Provides feedback and learns from outcomes

Prize targets:
  - Anthropic: Claude Agent SDK / Human Flourishing
  - Greylock: Best multi-turn agent (reasons about feedback, multi-step)
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from anthropic import Anthropic


# ---------------------------------------------------------------------------
# Tool definitions that Claude can call
# ---------------------------------------------------------------------------

AGENT_TOOLS = [
    {
        "name": "search_marketplace",
        "description": (
            "Search the Agent Workflow Marketplace for pre-solved reasoning workflows. "
            "Returns ranked results with similarity scores, ratings, token costs, and "
            "savings estimates. Use this when the user has a task that might already "
            "have a high-quality workflow available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language description of the task to search for",
                },
                "task_type": {
                    "type": "string",
                    "description": "Category: tax_filing, travel_planning, data_parsing, real_estate_search, outreach, shopping, product_comparison, etc.",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional hard filters: state, year, location, platform, domain",
                    "properties": {
                        "state": {"type": "string"},
                        "year": {"type": "integer"},
                        "location": {"type": "string"},
                        "platform": {"type": "string"},
                        "domain": {"type": "string"},
                    },
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "evaluate_workflow",
        "description": (
            "Deeply evaluate a specific workflow before purchasing. Returns the full "
            "workflow structure including steps, edge cases, domain knowledge, and "
            "token savings analysis. Use this to decide whether a workflow is worth buying."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "The workflow_id to evaluate",
                },
            },
            "required": ["workflow_id"],
        },
    },
    {
        "name": "purchase_workflow",
        "description": (
            "Purchase a workflow from the marketplace. Deducts token cost from the "
            "user's balance and returns the full execution template with all steps, "
            "placeholders, edge cases, and domain knowledge."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "The workflow_id to purchase",
                },
            },
            "required": ["workflow_id"],
        },
    },
    {
        "name": "execute_workflow_step",
        "description": (
            "Execute a single step of a purchased workflow. Fills in the user's "
            "private data into the template placeholders and performs the action. "
            "Returns the step result and any values extracted."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "The purchased workflow_id",
                },
                "step_number": {
                    "type": "integer",
                    "description": "Which step to execute (1-indexed)",
                },
                "user_data": {
                    "type": "object",
                    "description": "User's private data to fill into placeholders",
                },
            },
            "required": ["workflow_id", "step_number"],
        },
    },
    {
        "name": "rate_workflow",
        "description": (
            "Submit feedback on a purchased workflow after execution. Helps the "
            "marketplace surface better workflows. Include rating and optional comment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "The workflow_id to rate",
                },
                "rating": {
                    "type": "integer",
                    "description": "1-5 star rating",
                    "minimum": 1,
                    "maximum": 5,
                },
                "comment": {
                    "type": "string",
                    "description": "Optional feedback comment",
                },
                "tokens_actually_used": {
                    "type": "integer",
                    "description": "How many tokens the agent actually used executing the workflow",
                },
            },
            "required": ["workflow_id", "rating"],
        },
    },
    {
        "name": "estimate_complexity",
        "description": (
            "Estimate how complex a task is and whether it's worth querying the "
            "marketplace. Returns estimated tokens to solve from scratch vs. "
            "expected marketplace cost. Free to call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "Description of the task to estimate",
                },
            },
            "required": ["task_description"],
        },
    },
    {
        "name": "sanitize_query",
        "description": (
            "Sanitize a query by removing PII and bucketing sensitive data before "
            "sending to the marketplace. Returns the safe public query and keeps "
            "private data local. Privacy-first design."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "raw_data": {
                    "type": "object",
                    "description": "The raw data that may contain PII (names, SSN, exact income, etc.)",
                },
            },
            "required": ["raw_data"],
        },
    },
    {
        "name": "compare_products",
        "description": (
            "Compare products or services for a shopping/commerce task. "
            "Takes product criteria and returns a structured comparison. "
            "Used for commerce workflows."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Product category (electronics, clothing, food, etc.)",
                },
                "criteria": {
                    "type": "object",
                    "description": "What to optimize for: price, quality, reviews, etc.",
                },
                "budget": {
                    "type": "string",
                    "description": "Budget range",
                },
            },
            "required": ["category"],
        },
    },
]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Mark, an autonomous AI agent that helps users accomplish complex tasks efficiently by leveraging a marketplace of pre-solved reasoning workflows.

Your core capabilities:
1. **Task Analysis** — Understand what the user needs and estimate complexity
2. **Marketplace Search** — Find pre-built workflows that match the task using semantic + keyword search powered by Elasticsearch and JINA embeddings
3. **Smart Purchasing** — Evaluate workflow quality (rating, usage count, reviews) before buying
4. **Guided Execution** — Walk users through workflow steps, filling in their private data locally
5. **Feedback Loop** — Rate workflows after use to improve marketplace quality

Key principles:
- **Privacy First**: Always sanitize user data before marketplace queries. Names, SSN, exact income — NEVER sent to marketplace. Only anonymized task descriptors.
- **Token Efficiency**: Always estimate cost from scratch vs. marketplace. Only purchase a workflow if it saves significant tokens/time.
- **Human Flourishing**: Your goal is to make complex tasks (taxes, travel, shopping, real estate) accessible and stress-free for everyone.
- **Multi-turn Reasoning**: When a workflow doesn't fully apply, adapt. Combine insights from multiple workflows. Explain your reasoning.

When helping with commerce/shopping tasks:
- Compare products systematically
- Consider user's budget, preferences, and past behavior
- Optimize for value, not just lowest price
- Present options clearly with pros/cons

Always explain what you're doing and why. Be transparent about costs (token and time savings)."""


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class MarketplaceAgent:
    """
    Multi-turn autonomous agent powered by Claude.
    Manages conversation state, tool execution, and workflow lifecycle.
    """

    def __init__(
        self,
        elastic_client=None,
        sanitizer=None,
        anthropic_api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.elastic = elastic_client
        self.sanitizer = sanitizer

        # Session state
        self.conversation_history: List[Dict[str, Any]] = []
        self.purchased_workflows: Dict[str, Dict] = {}
        self.token_balance: int = 5000  # starting credits
        self.session_stats = {
            "searches": 0,
            "purchases": 0,
            "tokens_saved": 0,
            "workflows_rated": 0,
        }

    # ------------------------------------------------------------------
    # Tool execution (called when Claude uses a tool)
    # ------------------------------------------------------------------

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Route tool calls to the appropriate handler and return JSON result."""

        if tool_name == "search_marketplace":
            return self._tool_search(tool_input)
        elif tool_name == "evaluate_workflow":
            return self._tool_evaluate(tool_input)
        elif tool_name == "purchase_workflow":
            return self._tool_purchase(tool_input)
        elif tool_name == "execute_workflow_step":
            return self._tool_execute_step(tool_input)
        elif tool_name == "rate_workflow":
            return self._tool_rate(tool_input)
        elif tool_name == "estimate_complexity":
            return self._tool_estimate(tool_input)
        elif tool_name == "sanitize_query":
            return self._tool_sanitize(tool_input)
        elif tool_name == "compare_products":
            return self._tool_compare_products(tool_input)
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def _tool_search(self, inp: Dict) -> str:
        """Search Elasticsearch for matching workflows."""
        self.session_stats["searches"] += 1
        query_text = inp.get("query", "")
        filters = inp.get("filters", {})
        if inp.get("task_type"):
            filters["task_type"] = inp["task_type"]

        if self.elastic:
            try:
                results = self.elastic.hybrid_search(query_text, filters=filters, top_k=5)
                # Summarise for Claude
                summaries = []
                for r in results:
                    summaries.append({
                        "workflow_id": r.get("workflow_id"),
                        "title": r.get("title"),
                        "description": r.get("description", "")[:200],
                        "token_cost": r.get("token_cost"),
                        "rating": r.get("rating"),
                        "usage_count": r.get("usage_count"),
                        "match_percentage": r.get("match_percentage"),
                        "tags": r.get("tags", []),
                        "token_comparison": r.get("token_comparison"),
                    })
                return json.dumps({"results": summaries, "count": len(summaries)})
            except Exception as e:
                return json.dumps({"error": str(e), "results": []})
        else:
            return json.dumps({"error": "Elasticsearch not configured", "results": []})

    def _tool_evaluate(self, inp: Dict) -> str:
        """Get full workflow details for evaluation."""
        wf_id = inp["workflow_id"]
        if self.elastic:
            wf = self.elastic.get_by_id(wf_id)
            if wf:
                return json.dumps({
                    "workflow_id": wf["workflow_id"],
                    "title": wf.get("title"),
                    "description": wf.get("description"),
                    "steps_count": len(wf.get("steps", [])),
                    "steps_preview": [
                        {"step": s.get("step"), "thought": s.get("thought"), "action": s.get("action")}
                        for s in wf.get("steps", [])[:5]
                    ],
                    "edge_cases_count": len(wf.get("edge_cases", [])),
                    "domain_knowledge": wf.get("domain_knowledge", [])[:5],
                    "rating": wf.get("rating"),
                    "usage_count": wf.get("usage_count"),
                    "token_cost": wf.get("token_cost"),
                    "token_comparison": wf.get("token_comparison"),
                    "requirements": wf.get("requirements", []),
                })
            return json.dumps({"error": "Workflow not found"})
        return json.dumps({"error": "Elasticsearch not configured"})

    def _tool_purchase(self, inp: Dict) -> str:
        """Purchase a workflow — deduct tokens and store locally."""
        wf_id = inp["workflow_id"]
        if self.elastic:
            wf = self.elastic.get_by_id(wf_id)
            if not wf:
                return json.dumps({"error": "Workflow not found"})

            cost = wf.get("token_cost", 0)
            if self.token_balance < cost:
                return json.dumps({"error": "Insufficient token balance", "balance": self.token_balance, "cost": cost})

            self.token_balance -= cost
            self.purchased_workflows[wf_id] = wf
            self.session_stats["purchases"] += 1

            # Update usage count in Elasticsearch
            new_count = wf.get("usage_count", 0) + 1
            try:
                self.elastic.update_field(wf_id, "usage_count", new_count)
            except Exception:
                pass

            savings = wf.get("token_comparison", {})
            self.session_stats["tokens_saved"] += savings.get("from_scratch", 0) - savings.get("with_workflow", 0)

            return json.dumps({
                "success": True,
                "workflow_id": wf_id,
                "title": wf.get("title"),
                "token_cost": cost,
                "remaining_balance": self.token_balance,
                "steps_count": len(wf.get("steps", [])),
                "estimated_savings": savings,
            })
        return json.dumps({"error": "Elasticsearch not configured"})

    def _tool_execute_step(self, inp: Dict) -> str:
        """Execute a single step of a purchased workflow."""
        wf_id = inp["workflow_id"]
        step_num = inp["step_number"]
        user_data = inp.get("user_data", {})

        wf = self.purchased_workflows.get(wf_id)
        if not wf:
            return json.dumps({"error": "Workflow not purchased. Purchase it first."})

        steps = wf.get("steps", [])
        step = None
        for s in steps:
            if s.get("step") == step_num:
                step = s
                break

        if not step:
            return json.dumps({"error": f"Step {step_num} not found. Workflow has {len(steps)} steps."})

        # Fill placeholders with user data
        step_str = json.dumps(step)
        for key, value in user_data.items():
            step_str = step_str.replace(f"{{{key}}}", str(value))

        filled_step = json.loads(step_str)

        return json.dumps({
            "workflow_id": wf_id,
            "step": step_num,
            "total_steps": len(steps),
            "action": filled_step.get("action"),
            "thought": filled_step.get("thought"),
            "details": filled_step,
            "status": "executed",
            "note": "Step executed locally with user's private data. No PII was sent to marketplace.",
        })

    def _tool_rate(self, inp: Dict) -> str:
        """Submit feedback on a workflow."""
        wf_id = inp["workflow_id"]
        rating = inp["rating"]
        comment = inp.get("comment", "")
        tokens_used = inp.get("tokens_actually_used", 0)

        self.session_stats["workflows_rated"] += 1

        if self.elastic:
            wf = self.elastic.get_by_id(wf_id)
            if wf:
                old_rating = wf.get("rating", 5.0)
                new_rating = round((old_rating * 0.8 + rating * 0.2), 1)  # weighted average
                try:
                    self.elastic.update_field(wf_id, "rating", new_rating)
                except Exception:
                    pass

                return json.dumps({
                    "success": True,
                    "workflow_id": wf_id,
                    "your_rating": rating,
                    "new_average_rating": new_rating,
                    "comment": comment,
                    "tokens_actually_used": tokens_used,
                })

        return json.dumps({"success": True, "workflow_id": wf_id, "your_rating": rating})

    def _tool_estimate(self, inp: Dict) -> str:
        """Estimate task complexity."""
        desc = inp["task_description"].lower()

        # Heuristic complexity estimation
        complexity_signals = {
            "high": ["tax", "legal", "medical", "compliance", "multi-step", "regulation"],
            "medium": ["travel", "parsing", "analysis", "comparison", "outreach"],
            "low": ["simple", "lookup", "convert", "format"],
        }

        level = "medium"
        for lev, keywords in complexity_signals.items():
            if any(kw in desc for kw in keywords):
                level = lev
                break

        token_estimates = {"high": 3500, "medium": 2000, "low": 800}
        marketplace_cost = {"high": 200, "medium": 150, "low": 100}

        from_scratch = token_estimates[level]
        mkt_cost = marketplace_cost[level]

        return json.dumps({
            "complexity": level,
            "estimated_tokens_from_scratch": from_scratch,
            "estimated_marketplace_cost": mkt_cost,
            "estimated_savings_percent": int((1 - mkt_cost / from_scratch) * 100),
            "recommendation": "use_marketplace" if from_scratch > 1000 else "solve_directly",
        })

    def _tool_sanitize(self, inp: Dict) -> str:
        """Sanitize query through privacy layer."""
        raw_data = inp["raw_data"]
        if self.sanitizer:
            public, private = self.sanitizer.sanitize_query(raw_data)
            summary = self.sanitizer.get_sanitization_summary(raw_data, public)
            return json.dumps({
                "public_query": public,
                "fields_removed": summary.get("fields_removed", []),
                "fields_anonymized": summary.get("fields_anonymized", []),
                "pii_protected": True,
            })
        # Fallback: basic sanitization
        sensitive = ["name", "ssn", "email", "phone", "address", "social_security"]
        public = {k: v for k, v in raw_data.items() if not any(s in k.lower() for s in sensitive)}
        return json.dumps({"public_query": public, "pii_protected": True})

    def _tool_compare_products(self, inp: Dict) -> str:
        """Compare products for commerce tasks."""
        category = inp.get("category", "general")
        criteria = inp.get("criteria", {})
        budget = inp.get("budget", "any")

        return json.dumps({
            "category": category,
            "criteria": criteria,
            "budget": budget,
            "comparison_ready": True,
            "note": "Use a marketplace workflow for detailed product comparison in this category.",
            "suggestion": f"Search marketplace for '{category} product comparison' workflows.",
        })

    # ------------------------------------------------------------------
    # Main agent loop
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message through the multi-turn agent loop.
        Claude reasons, calls tools, and returns a final response.
        Returns dict with 'response', 'tool_calls', 'session_stats'.
        """
        if not self.client:
            return {
                "response": "Anthropic API key not configured. Set ANTHROPIC_API_KEY.",
                "tool_calls": [],
                "session_stats": self.session_stats,
            }

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        tool_calls_log: List[Dict] = []
        max_iterations = 10  # safety limit for tool loops

        for iteration in range(max_iterations):
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=AGENT_TOOLS,
                messages=self.conversation_history,
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Build assistant message with all content blocks
                assistant_content = []
                tool_uses = []

                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })
                        tool_uses.append(block)

                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content,
                })

                # Execute each tool and collect results
                tool_results = []
                for tool_use in tool_uses:
                    result = self._execute_tool(tool_use.name, tool_use.input)
                    tool_calls_log.append({
                        "tool": tool_use.name,
                        "input": tool_use.input,
                        "output_preview": result[:300],
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result,
                    })

                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results,
                })

            else:
                # Claude is done — extract final text
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_text,
                })

                return {
                    "response": final_text,
                    "tool_calls": tool_calls_log,
                    "session_stats": self.session_stats,
                    "token_balance": self.token_balance,
                    "iterations": iteration + 1,
                }

        # Safety: too many iterations
        return {
            "response": "Agent reached maximum reasoning iterations. Partial results may be available.",
            "tool_calls": tool_calls_log,
            "session_stats": self.session_stats,
            "token_balance": self.token_balance,
            "iterations": max_iterations,
        }

    def reset_session(self):
        """Reset conversation and session state."""
        self.conversation_history = []
        self.purchased_workflows = {}
        self.token_balance = 5000
        self.session_stats = {
            "searches": 0,
            "purchases": 0,
            "tokens_saved": 0,
            "workflows_rated": 0,
        }

    def get_session_summary(self) -> Dict[str, Any]:
        """Return current session state."""
        return {
            "token_balance": self.token_balance,
            "purchased_workflows": list(self.purchased_workflows.keys()),
            "conversation_turns": len([m for m in self.conversation_history if m["role"] == "user"]),
            "stats": self.session_stats,
        }
