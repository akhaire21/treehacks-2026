"""
scenarios.py — Pre-built simulation scenarios for frontend replay.

Each scenario contains the exact steps a Claude agent would take,
with realistic tool calls, results, and reasoning.
These power the /sdk frontend page without needing live API calls.
"""

SCENARIOS = {
    "tax_filing": {
        "id": "tax_filing",
        "title": "Ohio Tax Filing",
        "description": "Agent autonomously finds and purchases a tax workflow, then presents a step-by-step filing plan.",
        "icon": "📋",
        "prize": "Anthropic — Human Flourishing",
        "task": "Help me file my Ohio 2024 taxes. I have a W2 and want to use itemized deductions. Income around $85,000.",
        "steps": [
            {
                "thinking": "The user needs to file Ohio 2024 taxes with W2 income and itemized deductions. Let me search the marketplace for a matching workflow. I'll use mark_estimate which will automatically sanitize any PII before searching.",
                "tool_calls": [
                    {
                        "tool": "mark_estimate",
                        "input": {
                            "query": "File Ohio 2024 state taxes with W2 income and itemized deductions",
                            "context": {"state": "ohio", "year": 2024, "income_bracket": "80k-100k", "filing_type": "W2", "deduction_type": "itemized"}
                        },
                        "result": {
                            "session_id": "sess_demo_tax_001",
                            "num_solutions": 3,
                            "best_match": {
                                "solution_id": "sol_1",
                                "title": "Ohio IT-1040 (W2, Itemized) — Complete Filing Workflow",
                                "confidence": 0.94,
                                "pricing": {"total_cost_tokens": 500, "estimated_savings_percentage": 73},
                                "coverage": ["IT-1040", "Schedule A", "SD-100", "city tax"]
                            },
                            "alternatives": [
                                {"solution_id": "sol_2", "title": "Generic State Tax Filing", "confidence": 0.71, "pricing": {"total_cost_tokens": 300}},
                                {"solution_id": "sol_3", "title": "Ohio Simple Filing (Standard Deduction)", "confidence": 0.58, "pricing": {"total_cost_tokens": 200}}
                            ]
                        },
                        "latency_ms": 1200
                    }
                ],
                "latency_ms": 2100
            },
            {
                "thinking": "The marketplace found a highly relevant workflow — 94% confidence match for Ohio IT-1040 with W2 and itemized deductions. The cost is 500 tokens, which saves approximately 73% compared to solving from scratch. The coverage includes IT-1040, Schedule A, SD-100 (school district), and city tax. This is an excellent match. Let me purchase it.",
                "tool_calls": [
                    {
                        "tool": "mark_buy",
                        "input": {
                            "session_id": "sess_demo_tax_001",
                            "solution_id": "sol_1"
                        },
                        "result": {
                            "purchase_id": "purch_demo_001",
                            "tokens_charged": 500,
                            "execution_plan": {
                                "title": "Ohio IT-1040 (W2, Itemized) — Complete Filing Workflow",
                                "total_steps": 10,
                                "workflows": [
                                    {
                                        "workflow_id": "ohio_w2_itemized_2024",
                                        "title": "Ohio 2024 IT-1040 Filing",
                                        "steps": [
                                            {"step": 1, "action": "Gather W2 forms from all employers"},
                                            {"step": 2, "action": "Calculate Ohio Adjusted Gross Income (line 3)"},
                                            {"step": 3, "action": "Complete Schedule A — itemized deductions"},
                                            {"step": 4, "action": "Calculate Ohio taxable income (line 5)"},
                                            {"step": 5, "action": "Apply Ohio tax brackets (0.5% to 3.75%)"},
                                            {"step": 6, "action": "Calculate Joint Filing Credit if applicable"},
                                            {"step": 7, "action": "Complete SD-100 for school district tax"},
                                            {"step": 8, "action": "Check Columbus city tax (2.5% rate)"},
                                            {"step": 9, "action": "Apply withholding credits from W2 box 17"},
                                            {"step": 10, "action": "File electronically via Ohio eFile"}
                                        ],
                                        "edge_cases": [
                                            "Ohio does NOT have a $10,000 SALT cap — full deduction allowed",
                                            "Columbus residents must also file city RITA return",
                                            "School district tax varies — check SD# on W2 or use lookup tool"
                                        ],
                                        "domain_knowledge": [
                                            "Ohio has a graduated tax rate from 0% to 3.75% (2024)",
                                            "First $26,050 of income is tax-free for single filers",
                                            "Ohio Earned Income Credit = 30% of federal EIC"
                                        ]
                                    }
                                ]
                            }
                        },
                        "latency_ms": 800
                    }
                ],
                "latency_ms": 1800
            },
            {
                "thinking": "I've successfully purchased the workflow. Let me present the complete filing plan to the user, highlighting the key steps, edge cases, and domain knowledge. This workflow saved them significant time — they would have needed approximately 1,850 tokens to figure all of this out from scratch, but we got it for 500 tokens (73% savings). Let me also rate this workflow to help the marketplace.",
                "tool_calls": [
                    {
                        "tool": "mark_rate",
                        "input": {
                            "workflow_id": "ohio_w2_itemized_2024",
                            "rating": 5,
                            "vote": "up"
                        },
                        "result": {
                            "success": True,
                            "message": "Rating recorded. Thank you for improving the marketplace."
                        },
                        "latency_ms": 200
                    }
                ],
                "latency_ms": 1500
            }
        ],
        "final_response": "I found and purchased a comprehensive Ohio tax filing workflow for you. Here's your complete filing plan:\n\n**10-Step Filing Plan for Ohio IT-1040 (2024)**\n\n1. Gather W2 forms from all employers\n2. Calculate Ohio Adjusted Gross Income\n3. Complete Schedule A with itemized deductions\n4. Calculate Ohio taxable income\n5. Apply Ohio tax brackets (0.5% to 3.75%)\n6. Calculate Joint Filing Credit if applicable\n7. Complete SD-100 for school district tax\n8. Check Columbus city tax (2.5% rate)\n9. Apply withholding credits from W2 box 17\n10. File electronically via Ohio eFile\n\n**⚠️ Important Edge Cases:**\n- Ohio does NOT have a $10,000 SALT cap — you get the full deduction\n- As a Columbus resident, you'll also need to file a city RITA return\n- Check your school district number on your W2 for SD-100\n\n**💡 Domain Knowledge:**\n- Ohio's first $26,050 of income is tax-free for single filers\n- You may qualify for Ohio's Earned Income Credit (30% of federal)\n\n**Cost: 500 tokens (saved 73% vs. solving from scratch)**",
        "input_tokens": 2847,
        "output_tokens": 1923,
        "total_latency_ms": 5400
    },

    "shopping": {
        "id": "shopping",
        "title": "Smart Product Comparison",
        "description": "Agent finds a product comparison workflow, purchases it, and delivers structured recommendations.",
        "icon": "🛒",
        "prize": "Visa — Future of Commerce",
        "task": "I need to buy a laptop for software development, budget $1500-2000. Need 32GB RAM and a good screen.",
        "steps": [
            {
                "thinking": "The user needs a laptop for development with specific requirements. Let me search the marketplace for product comparison workflows that could help systematically evaluate options.",
                "tool_calls": [
                    {
                        "tool": "mark_estimate",
                        "input": {
                            "query": "Compare laptops for software development with specific specs: 32GB RAM, good display, $1500-2000 budget",
                            "context": {"category": "electronics", "product_type": "laptop", "use_case": "software_development"}
                        },
                        "result": {
                            "session_id": "sess_demo_shop_001",
                            "num_solutions": 2,
                            "best_match": {
                                "solution_id": "sol_1",
                                "title": "Developer Laptop Comparison Framework 2024",
                                "confidence": 0.87,
                                "pricing": {"total_cost_tokens": 350, "estimated_savings_percentage": 65}
                            }
                        },
                        "latency_ms": 950
                    }
                ],
                "latency_ms": 1800
            },
            {
                "thinking": "Good match at 87% confidence. The comparison framework costs 350 tokens and saves 65% vs. doing the research from scratch. Let me purchase it.",
                "tool_calls": [
                    {
                        "tool": "mark_buy",
                        "input": {
                            "session_id": "sess_demo_shop_001",
                            "solution_id": "sol_1"
                        },
                        "result": {
                            "purchase_id": "purch_demo_002",
                            "tokens_charged": 350,
                            "execution_plan": {
                                "title": "Developer Laptop Comparison Framework",
                                "workflows": [{
                                    "workflow_id": "dev_laptop_compare_2024",
                                    "title": "Developer Laptop Comparison",
                                    "steps": [
                                        {"step": 1, "action": "Define must-haves: RAM ≥32GB, display ≥14\", keyboard quality, build quality"},
                                        {"step": 2, "action": "Pull current models: MacBook Pro 14, ThinkPad X1 Carbon, Framework 16, Dell XPS 15"},
                                        {"step": 3, "action": "Score each on: dev performance, display quality, keyboard, portability, value"},
                                        {"step": 4, "action": "Check developer-specific factors: Linux support, Docker perf, terminal experience"},
                                        {"step": 5, "action": "Price check across Amazon, B&H, manufacturer direct"},
                                        {"step": 6, "action": "Factor in warranty, repair ecosystem, and resale value"}
                                    ],
                                    "edge_cases": [
                                        "M3 Pro MacBooks: 36GB unified memory counts as 32GB+ equivalent",
                                        "ThinkPad X1 Carbon Gen 12: max 64GB but soldered, not upgradeable",
                                        "Framework 16: upgradeable but GPU module adds $400+"
                                    ]
                                }]
                            }
                        },
                        "latency_ms": 700
                    }
                ],
                "latency_ms": 1600
            },
            {
                "thinking": "Great workflow. Let me rate it and present the structured comparison to the user.",
                "tool_calls": [
                    {
                        "tool": "mark_rate",
                        "input": {"workflow_id": "dev_laptop_compare_2024", "rating": 4, "vote": "up"},
                        "result": {"success": True}
                    }
                ],
                "latency_ms": 1200
            }
        ],
        "final_response": "Here's your structured laptop comparison based on the marketplace workflow:\n\n| Model | RAM | Display | Dev Score | Price |\n|-------|-----|---------|-----------|-------|\n| MacBook Pro 14\" M3 Pro | 36GB unified | 14.2\" Liquid Retina XDR | ⭐⭐⭐⭐⭐ | $1,999 |\n| ThinkPad X1 Carbon Gen 12 | 32GB | 14\" 2.8K OLED | ⭐⭐⭐⭐ | $1,649 |\n| Framework 16 | 32GB (upgradeable) | 16\" 2560x1600 | ⭐⭐⭐⭐ | $1,599 |\n| Dell XPS 15 | 32GB | 15.6\" 3.5K OLED | ⭐⭐⭐ | $1,799 |\n\n**My Recommendation:** MacBook Pro 14\" if you're in the Apple ecosystem, ThinkPad X1 Carbon if you need Linux.\n\n**Cost: 350 tokens (saved 65% vs. manual research)**",
        "input_tokens": 2100,
        "output_tokens": 1650,
        "total_latency_ms": 4600
    },

    "orchestrator": {
        "id": "orchestrator",
        "title": "Multi-Task Orchestration",
        "description": "Agent decomposes a complex relocation task into subtasks and chains marketplace workflows together.",
        "icon": "🔗",
        "prize": "Greylock — Best Multi-Turn Agent",
        "task": "I'm relocating from California to Ohio. Help with: 1) CA partial-year taxes, 2) Ohio tax setup, 3) Finding neighborhoods in Columbus.",
        "steps": [
            {
                "thinking": "This is a complex multi-domain request. I need to decompose it into 3 subtasks and check the marketplace for each one. Let me start with the California partial-year tax filing.",
                "tool_calls": [
                    {
                        "tool": "mark_estimate",
                        "input": {
                            "query": "File California partial-year resident taxes 2024 after relocating out of state",
                            "context": {"state": "california", "year": 2024, "filing_type": "partial_year"}
                        },
                        "result": {
                            "session_id": "sess_demo_orch_001",
                            "num_solutions": 2,
                            "best_match": {
                                "solution_id": "sol_1",
                                "title": "California Part-Year Resident Tax Filing",
                                "confidence": 0.89,
                                "pricing": {"total_cost_tokens": 450}
                            }
                        },
                        "latency_ms": 1100
                    }
                ],
                "latency_ms": 2000
            },
            {
                "thinking": "Found a strong match for CA partial-year taxes. Now let me check for Ohio tax setup workflows.",
                "tool_calls": [
                    {
                        "tool": "mark_estimate",
                        "input": {
                            "query": "Set up Ohio state tax withholding for new resident employee 2025",
                            "context": {"state": "ohio", "year": 2025, "task_type": "tax_setup"}
                        },
                        "result": {
                            "session_id": "sess_demo_orch_002",
                            "num_solutions": 2,
                            "best_match": {
                                "solution_id": "sol_1",
                                "title": "Ohio New Resident Tax Setup Guide",
                                "confidence": 0.82,
                                "pricing": {"total_cost_tokens": 300}
                            }
                        },
                        "latency_ms": 900
                    }
                ],
                "latency_ms": 1700
            },
            {
                "thinking": "Good match for Ohio setup too. Now let me check for Columbus neighborhood research.",
                "tool_calls": [
                    {
                        "tool": "mark_estimate",
                        "input": {
                            "query": "Find best family-friendly neighborhoods in Columbus Ohio for relocation",
                            "context": {"location": "Columbus, OH", "family_size": 4}
                        },
                        "result": {
                            "session_id": "sess_demo_orch_003",
                            "num_solutions": 1,
                            "best_match": {
                                "solution_id": "sol_1",
                                "title": "Columbus OH Neighborhood Guide for Families",
                                "confidence": 0.78,
                                "pricing": {"total_cost_tokens": 250}
                            }
                        },
                        "latency_ms": 850
                    }
                ],
                "latency_ms": 1600
            },
            {
                "thinking": "All 3 subtasks have marketplace coverage. Total cost would be 450 + 300 + 250 = 1,000 tokens. The California tax workflow is the most valuable (89% confidence), so let me buy the two tax workflows. For neighborhoods, I can supplement with my own knowledge. Let me buy the top 2.",
                "tool_calls": [
                    {
                        "tool": "mark_buy",
                        "input": {"session_id": "sess_demo_orch_001", "solution_id": "sol_1"},
                        "result": {
                            "purchase_id": "purch_demo_003",
                            "tokens_charged": 450,
                            "execution_plan": {
                                "title": "California Part-Year Resident Tax Filing",
                                "workflows": [{"workflow_id": "ca_partyear_2024", "title": "CA 540NR Filing", "steps": [
                                    {"step": 1, "action": "Determine CA-source income vs. total income"},
                                    {"step": 2, "action": "Complete Schedule CA (540NR) for income adjustments"},
                                    {"step": 3, "action": "Prorate deductions based on CA residency period"},
                                    {"step": 4, "action": "File Form 540NR (nonresident or part-year)"}
                                ]}]
                            }
                        },
                        "latency_ms": 750
                    },
                    {
                        "tool": "mark_buy",
                        "input": {"session_id": "sess_demo_orch_002", "solution_id": "sol_1"},
                        "result": {
                            "purchase_id": "purch_demo_004",
                            "tokens_charged": 300,
                            "execution_plan": {
                                "title": "Ohio New Resident Tax Setup",
                                "workflows": [{"workflow_id": "ohio_new_resident_2025", "title": "Ohio Tax Setup", "steps": [
                                    {"step": 1, "action": "File IT-4 with new employer for OH withholding"},
                                    {"step": 2, "action": "Register with Columbus RITA for city income tax"},
                                    {"step": 3, "action": "Determine school district for SD withholding"}
                                ]}]
                            }
                        },
                        "latency_ms": 600
                    }
                ],
                "latency_ms": 2200
            },
            {
                "thinking": "Both tax workflows purchased successfully. Total spent: 750 tokens. Let me rate both and deliver the comprehensive relocation plan.",
                "tool_calls": [
                    {
                        "tool": "mark_rate",
                        "input": {"workflow_id": "ca_partyear_2024", "rating": 5, "vote": "up"},
                        "result": {"success": True}
                    },
                    {
                        "tool": "mark_rate",
                        "input": {"workflow_id": "ohio_new_resident_2025", "rating": 4, "vote": "up"},
                        "result": {"success": True}
                    }
                ],
                "latency_ms": 1400
            }
        ],
        "final_response": "Here's your complete CA→OH relocation plan:\n\n**1. California Part-Year Taxes (540NR)**\n- Determine CA-source income vs. total\n- Complete Schedule CA (540NR)\n- Prorate deductions for CA residency period\n- File Form 540NR\n\n**2. Ohio Tax Setup**\n- File IT-4 with employer for OH withholding\n- Register with Columbus RITA (2.5% city tax)\n- Set up school district withholding\n\n**3. Columbus Neighborhoods (from my knowledge)**\n- 🏡 Upper Arlington — top schools, $450-600k homes\n- 🏡 Dublin — tech corridor, family-friendly, $400-550k\n- 🏡 Grandview Heights — walkable, closer to downtown, $350-500k\n- 🏡 Worthington — excellent schools, quieter, $350-475k\n\n**Marketplace cost: 750 tokens total (2 workflows purchased)**\n**Estimated savings: ~70% vs. researching from scratch**",
        "input_tokens": 4200,
        "output_tokens": 3100,
        "total_latency_ms": 8900
    }
}


def get_scenario(scenario_id: str) -> dict:
    """Get a simulation scenario by ID."""
    return SCENARIOS.get(scenario_id)


def list_scenarios() -> list:
    """List all available scenarios."""
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "description": s["description"],
            "icon": s["icon"],
            "prize": s["prize"],
            "task": s["task"],
        }
        for s in SCENARIOS.values()
    ]
