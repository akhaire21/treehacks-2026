'use client'

import { useState } from 'react'
import styles from './PricingBreakdown.module.css'

interface PricingData {
  price_tokens: number
  tokens_saved: number
  savings_percentage: number
  roi_percentage: number
  pricing: {
    base_price: number
    quality_multiplier: number
    market_rate?: number
    breakdown: string
  }
  avg_tokens_without: number
  avg_tokens_with: number
  rating: number
}

interface PricingBreakdownProps {
  workflowId: string
  title: string
  pricingData: PricingData
  compact?: boolean
}

export default function PricingBreakdown({
  workflowId,
  title,
  pricingData,
  compact = false,
}: PricingBreakdownProps) {
  const [showDetails, setShowDetails] = useState(false)

  const {
    price_tokens,
    tokens_saved,
    savings_percentage,
    roi_percentage,
    pricing,
    avg_tokens_without,
    avg_tokens_with,
    rating,
  } = pricingData

  if (compact) {
    return (
      <div className={styles.pricingCompact}>
        <div className={styles.priceTag}>
          <span className={styles.priceValue}>{price_tokens.toLocaleString()}</span>
          <span className={styles.priceLabel}>tokens</span>
        </div>
        <div className={styles.roiBadge}>
          <span className={styles.roiValue}>{roi_percentage.toLocaleString()}%</span>
          <span className={styles.roiLabel}>ROI</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.pricingBreakdown}>
      <div className={styles.pricingHeader}>
        <h3 className={styles.pricingTitle}>Pricing Breakdown</h3>
        <div className={styles.roiHighlight}>
          <div className={styles.roiMain}>
            <span className={styles.roiNumber}>{roi_percentage.toLocaleString()}%</span>
            <span className={styles.roiText}>ROI</span>
          </div>
          <div className={styles.roiSubtext}>Return on Investment</div>
        </div>
      </div>

      <div className={styles.pricingGrid}>
        <div className={styles.pricingCard}>
          <div className={styles.cardLabel}>Workflow Price</div>
          <div className={styles.cardValue}>
            <span className={styles.tokenIcon}>◈</span>
            {price_tokens.toLocaleString()} tokens
          </div>
          <div className={styles.cardSubtext}>One-time purchase cost</div>
        </div>

        <div className={styles.pricingCard}>
          <div className={styles.cardLabel}>Tokens Saved</div>
          <div className={`${styles.cardValue} ${styles.cardValueSuccess}`}>
            {tokens_saved.toLocaleString()} tokens
          </div>
          <div className={styles.cardSubtext}>{savings_percentage}% reduction vs. from scratch</div>
        </div>
      </div>

      <div className={styles.comparisonSection}>
        <div className={styles.comparisonTitle}>Token Usage Comparison</div>
        <div className={styles.comparisonBars}>
          <div className={styles.comparisonItem}>
            <div className={styles.comparisonLabel}>
              <span>Without workflow</span>
              <span className={styles.comparisonValue}>
                {avg_tokens_without.toLocaleString()} tokens
              </span>
            </div>
            <div className={styles.comparisonBar}>
              <div className={styles.comparisonBarFill} style={{ width: '100%' }}></div>
            </div>
          </div>
          <div className={styles.comparisonItem}>
            <div className={styles.comparisonLabel}>
              <span>With workflow</span>
              <span className={styles.comparisonValue}>
                {avg_tokens_with.toLocaleString()} tokens
              </span>
            </div>
            <div className={styles.comparisonBar}>
              <div
                className={`${styles.comparisonBarFill} ${styles.comparisonBarSuccess}`}
                style={{
                  width: `${(avg_tokens_with / avg_tokens_without) * 100}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <button
        className={styles.detailsToggle}
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? '▼ Hide' : '▶ Show'} pricing calculation details
      </button>

      {showDetails && (
        <div className={styles.calculationDetails}>
          <div className={styles.detailsTitle}>How is this price calculated?</div>

          <div className={styles.calculationStep}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepContent}>
              <div className={styles.stepTitle}>Base Price (15% of savings)</div>
              <div className={styles.stepFormula}>
                {tokens_saved.toLocaleString()} tokens saved × 0.15 = {pricing.base_price.toLocaleString()}{' '}
                tokens
              </div>
            </div>
          </div>

          <div className={styles.calculationStep}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepContent}>
              <div className={styles.stepTitle}>Quality Adjustment</div>
              <div className={styles.stepFormula}>
                Rating: {rating}★ → Multiplier: ×{pricing.quality_multiplier.toFixed(2)}
              </div>
              <div className={styles.stepExplanation}>
                Higher rated workflows (more proven, reliable) have higher prices
              </div>
            </div>
          </div>

          <div className={styles.calculationStep}>
            <div className={styles.stepNumber}>3</div>
            <div className={styles.stepContent}>
              <div className={styles.stepTitle}>Market Constraints</div>
              <div className={styles.stepFormula}>
                {pricing.market_rate
                  ? `Market rate: ${Math.round(pricing.market_rate)} tokens (±30% variance allowed)`
                  : 'No comparable workflows for market rate comparison'}
              </div>
              <div className={styles.stepExplanation}>
                Price stays within ±30% of similar workflows to ensure fairness
              </div>
            </div>
          </div>

          <div className={styles.calculationStep}>
            <div className={styles.stepNumber}>4</div>
            <div className={styles.stepContent}>
              <div className={styles.stepTitle}>Final Price</div>
              <div className={`${styles.stepFormula} ${styles.finalPrice}`}>
                <span className={styles.tokenIcon}>◈</span>
                {price_tokens.toLocaleString()} tokens
              </div>
            </div>
          </div>

          <div className={styles.breakdownSummary}>
            <div className={styles.summaryTitle}>Summary</div>
            <div className={styles.summaryText}>{pricing.breakdown}</div>
          </div>
        </div>
      )}

      <div className={styles.valueProposition}>
        <div className={styles.valueIcon}>✓</div>
        <div className={styles.valueText}>
          <strong>Value-based pricing:</strong> Pay {price_tokens.toLocaleString()} tokens to save{' '}
          {tokens_saved.toLocaleString()} tokens — that's a {roi_percentage.toLocaleString()}% return on
          your investment.
        </div>
      </div>
    </div>
  )
}
