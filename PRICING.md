# Dynamic Pricing Model Documentation

## Overview

The Agent Workflow Marketplace uses a transparent, value-based pricing model that ensures fair prices based on the value delivered (tokens saved) and quality (rating).

## Pricing Formula

### Base Formula
```
price = tokens_saved × 0.15 × quality_multiplier
```

### Quality Multiplier
```
quality_multiplier = 0.7 + (rating/5.0) × 0.6
```

This means:
- **5.0★ rating** → 1.3x multiplier
- **4.8★ rating** → 1.276x multiplier
- **4.0★ rating** → 1.18x multiplier
- **3.0★ rating** → 1.06x multiplier
- **1.0★ rating** → 0.82x multiplier

Higher-rated workflows command premium prices because they're more proven and reliable.

## Constraints

### Min/Max Bounds
- **Minimum price**: 50 tokens
- **Maximum price**: 2000 tokens

### Market Comparison
For similar workflows (same domain, similar token savings), prices stay within ±30% of the market median to ensure fairness.

## Real Examples

### Ohio Tax Filing Workflow
- **Without workflow**: 15,000 tokens
- **With workflow**: 4,650 tokens
- **Tokens saved**: 10,350 (69%)
- **Rating**: 4.8★
- **Quality multiplier**: 1.276x
- **Base price**: 1,552 tokens (15% of 10,350)
- **Final price**: 1,981 tokens
- **ROI**: 522% 🎯

### Tokyo Trip Planning Workflow
- **Without workflow**: 18,000 tokens
- **With workflow**: 4,860 tokens
- **Tokens saved**: 13,140 (73%)
- **Rating**: 4.7★
- **Quality multiplier**: 1.26x
- **Base price**: 1,971 tokens
- **Final price**: 2,000 tokens (capped at max)
- **ROI**: 657% 🚀

## Why This Model Works

### 1. Value-Based
You pay a percentage (~15%) of what you save. If a workflow saves you 10,000 tokens, you pay ~1,500 tokens.

### 2. Quality-Adjusted
Better workflows (higher ratings) cost more, incentivizing workflow creators to maintain quality.

### 3. Market-Constrained
Prices stay competitive within ±30% of similar workflows, preventing price gouging.

### 4. Transparent
Full pricing breakdown shown in UI:
```
Base: 1,552 (15% of 10,350 saved)
→ Quality adjusted (4.8★): ×1.28
→ Final: 1,981 tokens
```

## ROI Calculation

```
ROI = (tokens_saved / price) × 100
```

**Typical ROI**: 500-650%

This means for every 1 token spent, you save 5-6.5 tokens!

## Implementation

### Backend Module
File: `backend/pricing.py`

```python
from pricing import PricingEngine

# Calculate price for a workflow
pricing_result = PricingEngine.calculate_workflow_price(
    avg_tokens_without=15000,
    avg_tokens_with=4650,
    rating=4.8,
    comparable_prices=[1800, 1900, 2100]  # Optional
)

print(pricing_result['final_price'])  # 1981
print(pricing_result['roi_percentage'])  # 522.5
print(pricing_result['breakdown'])  # Full explanation
```

### Update Workflows
File: `backend/update_pricing.py`

Run this script to recalculate all workflow prices:
```bash
cd backend
python update_pricing.py
```

### API Endpoint
```bash
# Get pricing breakdown for a specific workflow
curl http://localhost:5001/api/pricing/ohio_w2_itemized_2024
```

Response:
```json
{
  "workflow_id": "ohio_w2_itemized_2024",
  "title": "Ohio 2024 IT-1040 (W2, Itemized, Married)",
  "price_tokens": 1981,
  "tokens_saved": 10350,
  "savings_percentage": 69,
  "roi_percentage": 522.5,
  "pricing": {
    "base_price": 1552,
    "quality_multiplier": 1.276,
    "market_rate": 1929.3,
    "breakdown": "Base: 1552 (15% of 10,350 saved) → Quality adjusted (4.8★): ×1.28 → Final: 1981 tokens"
  }
}
```

## Frontend Components

### PricingBreakdown Component
```tsx
import PricingBreakdown from '@/components/PricingBreakdown'

<PricingBreakdown
  workflowId="ohio_w2_itemized_2024"
  title="Ohio 2024 IT-1040"
  pricingData={{
    price_tokens: 1981,
    tokens_saved: 10350,
    savings_percentage: 69,
    roi_percentage: 522.5,
    pricing: { ... },
    avg_tokens_without: 15000,
    avg_tokens_with: 4650,
    rating: 4.8
  }}
/>
```

### Compact Display
```tsx
<PricingBreakdown
  {...props}
  compact={true}  // Shows just price and ROI badge
/>
```

## Workflow Data Structure

Each workflow in `workflows.json` includes:

```json
{
  "workflow_id": "ohio_w2_itemized_2024",
  "title": "...",
  "rating": 4.8,
  "avg_tokens_without": 15000,
  "avg_tokens_with": 4650,
  "tokens_saved": 10350,
  "savings_percentage": 69,
  "price_tokens": 1981,
  "pricing": {
    "base_price": 1552,
    "quality_multiplier": 1.276,
    "market_rate": 1929.3,
    "roi_percentage": 522.5,
    "breakdown": "..."
  }
}
```

## Modifying the Pricing Model

### Change Base Percentage
Edit `backend/pricing.py`:
```python
BASE_PERCENTAGE = 0.15  # Change from 15% to whatever you want
```

### Change Quality Multiplier Formula
Edit the `calculate_quality_multiplier` method:
```python
@staticmethod
def calculate_quality_multiplier(rating: float) -> float:
    # Current: 0.7 + (rating/5.0) × 0.6
    # Modify to suit your needs
    return 0.7 + (rating / 5.0) * 0.6
```

### Change Price Bounds
```python
MIN_PRICE = 50    # Minimum price in tokens
MAX_PRICE = 2000  # Maximum price in tokens
```

### Change Market Variance
```python
MARKET_VARIANCE_ALLOWED = 0.30  # ±30%, change as needed
```

After making changes, re-run `update_pricing.py` to recalculate all workflow prices.

## Testing

### Test Pricing Calculation
```python
from pricing import PricingEngine

# Test with different scenarios
test_cases = [
    (15000, 4650, 5.0),  # Perfect 5-star workflow
    (15000, 4650, 3.0),  # Average 3-star workflow
    (50000, 10000, 4.5), # High-value workflow (will hit max price)
]

for without, with_wf, rating in test_cases:
    result = PricingEngine.calculate_workflow_price(without, with_wf, rating)
    print(f"Rating {rating}★: Price={result['final_price']}, ROI={result['roi_percentage']}%")
```

## UI Views

### Marketplace Page
`http://localhost:3000/marketplace`

Browse all workflows with:
- Price display
- ROI badges
- Expandable pricing breakdowns
- Filter by task type
- Marketplace stats (total workflows, avg ROI, etc.)

### Individual Workflow
Click "Show Pricing Details" on any workflow card to see:
- Full pricing breakdown
- Step-by-step calculation
- Token usage comparison chart
- Value proposition summary

---

Built with transparency and fairness in mind. Questions? Check `backend/pricing.py` for implementation details.
