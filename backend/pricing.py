"""
Dynamic Pricing Engine for Agent Workflow Marketplace.
Calculates workflow prices based on value delivered and quality.
"""

from typing import Dict, List, Optional
import statistics


class PricingEngine:
    """
    Calculates dynamic pricing for workflows based on:
    - Tokens saved (value delivered)
    - Quality rating (performance multiplier)
    - Market comparables (fairness constraint)
    """

    # Pricing constraints
    MIN_PRICE = 50
    MAX_PRICE = 2000
    BASE_PERCENTAGE = 0.15  # 15% of tokens saved
    MARKET_VARIANCE_ALLOWED = 0.30  # ±30%

    @staticmethod
    def calculate_quality_multiplier(rating: float) -> float:
        """
        Calculate quality multiplier from rating.
        Formula: 0.7 + (rating/5.0) × 0.6

        Examples:
        - 5.0★ → 1.3x
        - 4.8★ → 1.276x
        - 4.0★ → 1.18x
        - 3.0★ → 1.06x
        - 1.0★ → 0.82x
        """
        return 0.7 + (rating / 5.0) * 0.6

    @staticmethod
    def calculate_base_price(tokens_saved: int, rating: float) -> int:
        """
        Calculate base price using the formula:
        price = tokens_saved × 0.15 × quality_multiplier
        """
        quality_multiplier = PricingEngine.calculate_quality_multiplier(rating)
        base_price = tokens_saved * PricingEngine.BASE_PERCENTAGE * quality_multiplier
        return int(round(base_price))

    @staticmethod
    def constrain_price(price: int) -> int:
        """Apply min/max constraints to price."""
        return max(PricingEngine.MIN_PRICE, min(price, PricingEngine.MAX_PRICE))

    @staticmethod
    def calculate_market_rate(comparable_prices: List[int]) -> Optional[float]:
        """Calculate median price of comparable workflows."""
        if not comparable_prices:
            return None
        return statistics.median(comparable_prices)

    @staticmethod
    def apply_market_constraint(
        price: int,
        market_rate: Optional[float]
    ) -> int:
        """
        Ensure price stays within ±30% of market rate for similar workflows.
        """
        if market_rate is None:
            return price

        min_market = market_rate * (1 - PricingEngine.MARKET_VARIANCE_ALLOWED)
        max_market = market_rate * (1 + PricingEngine.MARKET_VARIANCE_ALLOWED)

        return int(round(max(min_market, min(price, max_market))))

    @staticmethod
    def calculate_workflow_price(
        avg_tokens_without: int,
        avg_tokens_with: int,
        rating: float,
        comparable_prices: Optional[List[int]] = None
    ) -> Dict:
        """
        Calculate complete pricing breakdown for a workflow.

        Returns:
        {
            'tokens_saved': int,
            'base_price': int,
            'quality_multiplier': float,
            'constrained_price': int,
            'market_rate': float or None,
            'final_price': int,
            'roi_percentage': float,
            'breakdown': str
        }
        """
        # Calculate tokens saved
        tokens_saved = avg_tokens_without - avg_tokens_with

        # Calculate quality multiplier
        quality_multiplier = PricingEngine.calculate_quality_multiplier(rating)

        # Calculate base price (15% of savings × quality)
        base_amount = int(tokens_saved * PricingEngine.BASE_PERCENTAGE)
        base_price = PricingEngine.calculate_base_price(tokens_saved, rating)

        # Apply min/max constraints
        constrained_price = PricingEngine.constrain_price(base_price)

        # Calculate market rate and apply market constraint
        market_rate = PricingEngine.calculate_market_rate(comparable_prices) if comparable_prices else None
        final_price = PricingEngine.apply_market_constraint(constrained_price, market_rate)

        # Calculate ROI
        roi_percentage = (tokens_saved / final_price * 100) if final_price > 0 else 0

        # Create breakdown string
        breakdown = (
            f"Base: {base_amount} (15% of {tokens_saved:,} saved) → "
            f"Quality adjusted ({rating}★): ×{quality_multiplier:.2f} → "
            f"Final: {final_price} tokens"
        )

        return {
            'tokens_saved': tokens_saved,
            'base_price': base_price,
            'quality_multiplier': quality_multiplier,
            'constrained_price': constrained_price,
            'market_rate': market_rate,
            'final_price': final_price,
            'roi_percentage': round(roi_percentage, 1),
            'breakdown': breakdown
        }

    @staticmethod
    def get_comparable_workflows(
        all_workflows: List[Dict],
        target_workflow_id: str,
        task_type: str,
        tokens_saved_tolerance: float = 0.3
    ) -> List[int]:
        """
        Find comparable workflows for market rate calculation.
        Compares workflows with same task_type and similar tokens_saved (±30%).
        """
        comparable_prices = []

        # Find the target workflow
        target = None
        for w in all_workflows:
            if w.get('workflow_id') == target_workflow_id:
                target = w
                break

        if not target:
            return comparable_prices

        target_tokens_saved = target.get('tokens_saved', 0)
        if target_tokens_saved == 0:
            return comparable_prices

        # Find comparable workflows
        for workflow in all_workflows:
            # Skip self
            if workflow.get('workflow_id') == target_workflow_id:
                continue

            # Must be same task type
            if workflow.get('task_type') != task_type:
                continue

            # Must have similar tokens saved (±30%)
            w_tokens_saved = workflow.get('tokens_saved', 0)
            if w_tokens_saved == 0:
                continue

            ratio = w_tokens_saved / target_tokens_saved
            if 1 - tokens_saved_tolerance <= ratio <= 1 + tokens_saved_tolerance:
                price = workflow.get('price_tokens')
                if price:
                    comparable_prices.append(price)

        return comparable_prices


def calculate_token_savings_percentage(avg_tokens_without: int, avg_tokens_with: int) -> int:
    """Calculate percentage of tokens saved."""
    if avg_tokens_without == 0:
        return 0
    tokens_saved = avg_tokens_without - avg_tokens_with
    return int((tokens_saved / avg_tokens_without) * 100)
