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
    # Based on token savings percentages in the README
    workflow_token_data = {
        'ohio_w2_itemized_2024': {
            'avg_tokens_without': 15000,
            'avg_tokens_with': 4650,  # 69% savings
            'savings_pct': 69
        },
        'california_w2_standard_2024': {
            'avg_tokens_without': 14500,
            'avg_tokens_with': 4785,  # 67% savings
            'savings_pct': 67
        },
        'tokyo_family_trip_5day': {
            'avg_tokens_without': 18000,
            'avg_tokens_with': 4860,  # 73% savings
            'savings_pct': 73
        },
        'stripe_invoice_parser_multicurrency': {
            'avg_tokens_without': 12000,
            'avg_tokens_with': 4080,  # 66% savings
            'savings_pct': 66
        },
        'zillow_columbus_homes_search': {
            'avg_tokens_without': 13500,
            'avg_tokens_with': 4725,  # 65% savings
            'savings_pct': 65
        },
        'linkedin_b2b_cold_outreach': {
            'avg_tokens_without': 11000,
            'avg_tokens_with': 4400,  # 60% savings
            'savings_pct': 60
        },
        'nebraska_selfemployed_quarterly_2024': {
            'avg_tokens_without': 16000,
            'avg_tokens_with': 4800,  # 70% savings
            'savings_pct': 70
        },
        'pdf_medical_records_parser': {
            'avg_tokens_without': 13000,
            'avg_tokens_with': 4550,  # 65% savings
            'savings_pct': 65
        }
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
