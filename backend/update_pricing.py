"""
Script to update workflows.json with dynamic pricing data.
Run this once to add pricing fields to all workflows.
"""

import json
from pricing import PricingEngine, calculate_token_savings_percentage


def update_workflows_with_pricing():
    """Update all workflows with comprehensive pricing data."""

    # Load existing workflows
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workflows_path = os.path.join(script_dir, 'workflows.json')

    with open(workflows_path, 'r') as f:
        data = json.load(f)

    workflows = data['workflows']

    # Define baseline token costs for each workflow
    # Based on complexity: Simple (8-10k), Medium (12-16k), Complex (18-25k), Very Complex (25-35k)
    workflow_token_data = {
        # Original 8 workflows
        'ohio_w2_itemized_2024': {
            'avg_tokens_without': 15000,
            'avg_tokens_with': 4650,
            'savings_pct': 69
        },
        'california_w2_standard_2024': {
            'avg_tokens_without': 14500,
            'avg_tokens_with': 4785,
            'savings_pct': 67
        },
        'tokyo_family_trip_5day': {
            'avg_tokens_without': 18000,
            'avg_tokens_with': 4860,
            'savings_pct': 73
        },
        'stripe_invoice_parser_multicurrency': {
            'avg_tokens_without': 12000,
            'avg_tokens_with': 4080,
            'savings_pct': 66
        },
        'zillow_columbus_homes_search': {
            'avg_tokens_without': 13500,
            'avg_tokens_with': 4725,
            'savings_pct': 65
        },
        'linkedin_b2b_cold_outreach': {
            'avg_tokens_without': 11000,
            'avg_tokens_with': 4400,
            'savings_pct': 60
        },
        'nebraska_selfemployed_quarterly_2024': {
            'avg_tokens_without': 16000,
            'avg_tokens_with': 4800,
            'savings_pct': 70
        },
        'pdf_medical_records_parser': {
            'avg_tokens_without': 13000,
            'avg_tokens_with': 4550,
            'savings_pct': 65
        },

        # Very Complex workflows (25k-35k tokens without)
        'ma_due_diligence_vdr_scanner_2026': {
            'avg_tokens_without': 32000,
            'avg_tokens_with': 7360,
            'savings_pct': 77
        },
        'legacy_monolith_microservices_extractor': {
            'avg_tokens_without': 28000,
            'avg_tokens_with': 6440,
            'savings_pct': 77
        },
        'clinical_trial_patient_screening_hipaa': {
            'avg_tokens_without': 26000,
            'avg_tokens_with': 6240,
            'savings_pct': 76
        },
        'automated_pentest_webapp_owasp': {
            'avg_tokens_without': 30000,
            'avg_tokens_with': 6900,
            'savings_pct': 77
        },
        'patent_prior_art_semantic_search': {
            'avg_tokens_without': 24000,
            'avg_tokens_with': 6000,
            'savings_pct': 75
        },
        'gdnt_engineering_drawing_checker': {
            'avg_tokens_without': 27000,
            'avg_tokens_with': 6210,
            'savings_pct': 77
        },

        # Complex workflows (18k-24k tokens without)
        'supply_chain_predictive_inventory_q4': {
            'avg_tokens_without': 22000,
            'avg_tokens_with': 5720,
            'savings_pct': 74
        },
        'crypto_portfolio_rebalancer_harvesting': {
            'avg_tokens_without': 20000,
            'avg_tokens_with': 5400,
            'savings_pct': 73
        },
        'corporate_travel_policy_auditor': {
            'avg_tokens_without': 19000,
            'avg_tokens_with': 5320,
            'savings_pct': 72
        },
        'real_estate_brrrr_calculator': {
            'avg_tokens_without': 21000,
            'avg_tokens_with': 5670,
            'savings_pct': 73
        },
        'wedding_budget_vendor_manager_luxury': {
            'avg_tokens_without': 18000,
            'avg_tokens_with': 5220,
            'savings_pct': 71
        },

        # Medium workflows (12k-17k tokens without)
        'seo_topic_cluster_authority_builder': {
            'avg_tokens_without': 16000,
            'avg_tokens_with': 4640,
            'savings_pct': 71
        },
        'podcast_post_production_repurposing': {
            'avg_tokens_without': 15000,
            'avg_tokens_with': 4500,
            'savings_pct': 70
        },
        'personalized_sleep_circadian_optimization': {
            'avg_tokens_without': 14000,
            'avg_tokens_with': 4340,
            'savings_pct': 69
        },
        'academic_grant_proposal_generator': {
            'avg_tokens_without': 17000,
            'avg_tokens_with': 4930,
            'savings_pct': 71
        },
        'subscription_audit_optimizer': {
            'avg_tokens_without': 12000,
            'avg_tokens_with': 3840,
            'savings_pct': 68
        },

        # Simple workflows (8k-11k tokens without)
        'smart_grocery_optimizer': {
            'avg_tokens_without': 9000,
            'avg_tokens_with': 3510,
            'savings_pct': 61
        },
        'electronics_purchase_advisor': {
            'avg_tokens_without': 10000,
            'avg_tokens_with': 3700,
            'savings_pct': 63
        },
        'fashion_personal_shopper': {
            'avg_tokens_without': 8500,
            'avg_tokens_with': 3315,
            'savings_pct': 61
        },

        # AI-specific workflows (15k-25k tokens without)
        'ai_code_refactor_legacy': {
            'avg_tokens_without': 22000,
            'avg_tokens_with': 5940,
            'savings_pct': 73
        },
        'ai_api_integration_auto': {
            'avg_tokens_without': 18000,
            'avg_tokens_with': 5040,
            'savings_pct': 72
        },
        'ai_data_pipeline_builder': {
            'avg_tokens_without': 20000,
            'avg_tokens_with': 5600,
            'savings_pct': 72
        },
        'ai_security_audit_continuous': {
            'avg_tokens_without': 24000,
            'avg_tokens_with': 6480,
            'savings_pct': 73
        },
        'ai_test_generation_comprehensive': {
            'avg_tokens_without': 19000,
            'avg_tokens_with': 5320,
            'savings_pct': 72
        },
        'ai_database_optimization': {
            'avg_tokens_without': 21000,
            'avg_tokens_with': 5880,
            'savings_pct': 72
        },
        'ai_incident_response': {
            'avg_tokens_without': 23000,
            'avg_tokens_with': 6210,
            'savings_pct': 73
        },
        'ai_code_review_intelligent': {
            'avg_tokens_without': 17000,
            'avg_tokens_with': 4930,
            'savings_pct': 71
        },
        'ai_documentation_auto_generation': {
            'avg_tokens_without': 15000,
            'avg_tokens_with': 4500,
            'savings_pct': 70
        },
        'ai_research_synthesis': {
            'avg_tokens_without': 16000,
            'avg_tokens_with': 4640,
            'savings_pct': 71
        },
    }

    # First pass: Update all workflows with token data
    for workflow in workflows:
        workflow_id = workflow['workflow_id']

        if workflow_id in workflow_token_data:
            token_data = workflow_token_data[workflow_id]
            workflow['avg_tokens_without'] = token_data['avg_tokens_without']
            workflow['avg_tokens_with'] = token_data['avg_tokens_with']
            workflow['tokens_saved'] = token_data['avg_tokens_without'] - token_data['avg_tokens_with']
            workflow['savings_percentage'] = token_data['savings_pct']

    # Second pass: Calculate prices (now that we have all token data)
    for workflow in workflows:
        workflow_id = workflow['workflow_id']
        rating = workflow['rating']

        # Find comparable workflows for market rate
        comparable_prices = PricingEngine.get_comparable_workflows(
            workflows,
            workflow_id,
            workflow['task_type']
        )

        # Calculate pricing
        pricing_result = PricingEngine.calculate_workflow_price(
            workflow['avg_tokens_without'],
            workflow['avg_tokens_with'],
            rating,
            comparable_prices if comparable_prices else None
        )

        # Update workflow with pricing data
        workflow['price_tokens'] = pricing_result['final_price']
        workflow['pricing'] = {
            'base_price': pricing_result['base_price'],
            'quality_multiplier': round(pricing_result['quality_multiplier'], 3),
            'market_rate': pricing_result['market_rate'],
            'roi_percentage': pricing_result['roi_percentage'],
            'breakdown': pricing_result['breakdown']
        }

        # Keep execution_tokens separate (tokens used when executing workflow)
        # This is different from price_tokens (cost to purchase)
        if 'execution_tokens' not in workflow:
            workflow['execution_tokens'] = workflow['avg_tokens_with']

    # Save updated workflows
    with open(workflows_path, 'w') as f:
        json.dump(data, f, indent=2)

    print("✅ Updated workflows.json with dynamic pricing data")
    print("\nPricing Summary:")
    print("-" * 80)

    for workflow in workflows:
        print(f"\n{workflow['title']}")
        print(f"  Rating: {workflow['rating']}★")
        print(f"  Tokens saved: {workflow['tokens_saved']:,} ({workflow['savings_percentage']}%)")
        print(f"  Price: {workflow['price_tokens']} tokens")
        print(f"  ROI: {workflow['pricing']['roi_percentage']:,.1f}%")
        print(f"  {workflow['pricing']['breakdown']}")


if __name__ == '__main__':
    update_workflows_with_pricing()
