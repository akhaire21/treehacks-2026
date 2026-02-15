'use client'

import { useState } from 'react'
import styles from './WorkflowCard.module.css'
import PricingBreakdown from './PricingBreakdown'

interface Workflow {
  workflow_id: string
  title: string
  description: string
  task_type: string
  price_tokens: number
  tokens_saved: number
  savings_percentage: number
  rating: number
  usage_count: number
  tags: string[]
  pricing?: {
    base_price: number
    quality_multiplier: number
    market_rate?: number
    roi_percentage: number
    breakdown: string
  }
  avg_tokens_without: number
  avg_tokens_with: number
}

interface WorkflowCardProps {
  workflow: Workflow
  onPurchase?: (workflowId: string) => void
}

export default function WorkflowCard({ workflow, onPurchase }: WorkflowCardProps) {
  const [showPricing, setShowPricing] = useState(false)

  const {
    workflow_id,
    title,
    description,
    price_tokens = 0,
    tokens_saved = 0,
    savings_percentage = 0,
    rating = 0,
    usage_count = 0,
    tags = [],
    pricing,
    avg_tokens_without = 0,
    avg_tokens_with = 0,
  } = workflow

  const roiPercentage = pricing?.roi_percentage || 0
  const hasFullPricingData = !!(pricing && avg_tokens_without > 0 && avg_tokens_with > 0)

  return (
    <div className={styles.workflowCard}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>{title}</div>
        <div className={styles.cardStats}>
          <div className={styles.statItem}>
            <span className={styles.statIcon}>★</span>
            <span className={styles.statValue}>{rating}</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statIcon}>↗</span>
            <span className={styles.statValue}>{usage_count}</span>
          </div>
        </div>
      </div>

      <p className={styles.cardDescription}>{description}</p>

      <div className={styles.cardTags}>
        {tags.map((tag) => (
          <span key={tag} className={styles.tag}>
            {tag}
          </span>
        ))}
      </div>

      <div className={styles.cardMetrics}>
        <div className={styles.metricItem}>
          <div className={styles.metricLabel}>Tokens Saved</div>
          <div className={styles.metricValue}>
            {tokens_saved?.toLocaleString() || 'N/A'}
            <span className={styles.metricBadge}>{savings_percentage}%</span>
          </div>
        </div>
      </div>

      <div className={styles.cardPricing}>
        <div className={styles.priceSection}>
          <div className={styles.priceLabel}>Price</div>
          <div className={styles.priceValue}>
            <span className={styles.tokenIcon}>◈</span>
            {price_tokens.toLocaleString()}
          </div>
        </div>
        <div className={styles.roiSection}>
          <div className={styles.roiLabel}>ROI</div>
          <div className={styles.roiValue}>{roiPercentage.toLocaleString()}%</div>
        </div>
      </div>

      <div className={styles.cardActions}>
        <button
          className={styles.btnPrimary}
          onClick={() => onPurchase && onPurchase(workflow_id)}
        >
          Purchase Workflow
        </button>
        <button className={styles.btnSecondary} onClick={() => setShowPricing(!showPricing)}>
          {showPricing ? 'Hide' : 'Show'} Pricing Details
        </button>
      </div>

      {showPricing && hasFullPricingData && (
        <div className={styles.pricingDetails}>
          <PricingBreakdown
            workflowId={workflow_id}
            title={title}
            pricingData={{
              price_tokens,
              tokens_saved,
              savings_percentage,
              roi_percentage: roiPercentage,
              pricing: pricing!,
              avg_tokens_without,
              avg_tokens_with,
              rating,
            }}
          />
        </div>
      )}

      {showPricing && !hasFullPricingData && (
        <div className={styles.pricingDetails}>
          <div style={{ padding: '1rem', background: 'var(--surface-2)', borderRadius: '8px', fontSize: '0.875rem', color: 'var(--text-dim)' }}>
            <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text)' }}>Pricing Summary</div>
            <div>Price: <strong style={{ color: 'var(--accent)' }}>◈ {price_tokens.toLocaleString()}</strong> tokens</div>
            {tokens_saved > 0 && <div>Tokens saved: <strong style={{ color: 'var(--green)' }}>{tokens_saved.toLocaleString()}</strong> ({savings_percentage}% reduction)</div>}
            {roiPercentage > 0 && <div>ROI: <strong style={{ color: 'var(--green)' }}>{roiPercentage.toLocaleString()}%</strong></div>}
            {pricing?.breakdown && <div style={{ marginTop: '0.5rem', opacity: 0.8 }}>{pricing.breakdown}</div>}
          </div>
        </div>
      )}
    </div>
  )
}
