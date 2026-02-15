'use client'

import { useEffect, useState } from 'react'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'
import WorkflowCard from '@/components/WorkflowCard'
import PurchaseModal from '@/components/PurchaseModal'
import styles from './marketplace.module.css'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

interface RawWorkflow {
  workflow_id: string
  title: string
  description: string
  task_type: string
  rating: number
  usage_count: number
  tags: string[]
  token_cost?: number
  execution_tokens?: number
  token_comparison?: {
    from_scratch: number
    with_workflow: number
  }
  // These may or may not come from backend
  price_tokens?: number
  tokens_saved?: number
  savings_percentage?: number
  avg_tokens_without?: number
  avg_tokens_with?: number
  pricing?: {
    base_price: number
    quality_multiplier: number
    market_rate?: number
    roi_percentage: number
    breakdown: string
  }
}

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

/** Compute pricing fields client-side from raw API data */
function enrichWorkflow(raw: RawWorkflow): Workflow {
  const rating = raw.rating || 4.0

  // Derive avg_tokens_without & avg_tokens_with
  let avg_tokens_with = raw.avg_tokens_with || 0
  let avg_tokens_without = raw.avg_tokens_without || 0

  if (!avg_tokens_with && raw.token_comparison?.with_workflow) {
    avg_tokens_with = raw.token_comparison.with_workflow
  }
  if (!avg_tokens_without && raw.token_comparison?.from_scratch) {
    avg_tokens_without = raw.token_comparison.from_scratch
  }
  if (!avg_tokens_with && raw.execution_tokens) {
    avg_tokens_with = raw.execution_tokens
  }
  if (!avg_tokens_without && avg_tokens_with > 0) {
    avg_tokens_without = Math.round(avg_tokens_with * 3.2)
  }

  // Tokens saved
  const tokens_saved = raw.tokens_saved || Math.max(0, avg_tokens_without - avg_tokens_with)

  // Savings percentage
  const savings_percentage =
    raw.savings_percentage ||
    (avg_tokens_without > 0 ? Math.round((tokens_saved / avg_tokens_without) * 100) : 0)

  // Price: prefer existing, then token_cost, then calculate
  let price_tokens = raw.price_tokens || raw.token_cost || 0
  if (!price_tokens && tokens_saved > 0) {
    const qualityMultiplier = 0.7 + (rating / 5.0) * 0.6
    price_tokens = Math.max(50, Math.min(2000, Math.round(tokens_saved * 0.15 * qualityMultiplier)))
  }

  // ROI
  const roi_percentage =
    price_tokens > 0 ? Math.round((tokens_saved / price_tokens) * 100 * 10) / 10 : 0

  // Quality multiplier
  const qualityMultiplier = 0.7 + (rating / 5.0) * 0.6
  const base_price = Math.round(tokens_saved * 0.15)

  const pricing = raw.pricing || (tokens_saved > 0
    ? {
        base_price,
        quality_multiplier: Math.round(qualityMultiplier * 1000) / 1000,
        market_rate: undefined as number | undefined,
        roi_percentage,
        breakdown: `Base: ${base_price.toLocaleString()} (15% of ${tokens_saved.toLocaleString()} saved) → Quality adjusted (${rating}★): ×${qualityMultiplier.toFixed(2)} → Final: ${price_tokens.toLocaleString()} tokens`,
      }
    : undefined)

  return {
    workflow_id: raw.workflow_id,
    title: raw.title,
    description: raw.description,
    task_type: raw.task_type,
    rating,
    usage_count: raw.usage_count || 0,
    tags: raw.tags || [],
    price_tokens,
    tokens_saved,
    savings_percentage,
    avg_tokens_without,
    avg_tokens_with,
    pricing,
  }
}

export default function MarketplacePage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [purchasingWorkflow, setPurchasingWorkflow] = useState<Workflow | null>(null)
  const [purchasedIds, setPurchasedIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows`)
      if (!response.ok) {
        throw new Error('Failed to fetch workflows')
      }
      const data = await response.json()
      const enriched = (data.workflows || []).map(enrichWorkflow)
      setWorkflows(enriched)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = (workflowId: string) => {
    const wf = workflows.find((w) => w.workflow_id === workflowId)
    if (wf) setPurchasingWorkflow(wf)
  }

  const handlePurchaseSuccess = (data: any) => {
    setPurchasedIds((prev) => new Set([...prev, data.receipt?.workflow_id || data.workflow?.workflow_id || '']))
  }

  const taskTypes = ['all', ...new Set(workflows.map((w) => w.task_type))]

  const filteredWorkflows =
    filter === 'all' ? workflows : workflows.filter((w) => w.task_type === filter)

  // Calculate marketplace stats
  const totalWorkflows = workflows.length
  const totalTokensSaved = workflows.reduce((sum, w) => sum + (w.tokens_saved || 0), 0)
  const avgROI =
    workflows.length > 0
      ? Math.round(
          workflows.reduce((sum, w) => sum + (w.pricing?.roi_percentage || 0), 0) /
            workflows.length
        )
      : 0
  const totalPurchases = workflows.reduce((sum, w) => sum + w.usage_count, 0)

  if (loading) {
    return (
      <>
        <Nav />
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading marketplace...</p>
        </div>
        <Footer />
      </>
    )
  }

  if (error) {
    return (
      <>
        <Nav />
        <div className={styles.error}>
          <h2>Error Loading Marketplace</h2>
          <p>{error}</p>
          <p className={styles.errorHelp}>
            Make sure the backend API is running on <code>http://localhost:5001</code>
          </p>
          <button onClick={fetchWorkflows} className={styles.retryButton}>
            Retry
          </button>
        </div>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Nav />
      <main className={styles.marketplacePage}>
        <div className={styles.hero}>
          <h1 className={styles.title}>Workflow Marketplace</h1>
          <p className={styles.subtitle}>
            Browse proven AI agent workflows. Pay once, save thousands of tokens.
          </p>
        </div>

        <div className={styles.stats}>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{totalWorkflows}</div>
            <div className={styles.statLabel}>Workflows</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{totalTokensSaved.toLocaleString()}</div>
            <div className={styles.statLabel}>Total Tokens Saved</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{avgROI}%</div>
            <div className={styles.statLabel}>Average ROI</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{totalPurchases}</div>
            <div className={styles.statLabel}>Total Purchases</div>
          </div>
        </div>

        <div className={styles.container}>
          <div className={styles.filters}>
            <div className={styles.filterLabel}>Filter by type:</div>
            <div className={styles.filterButtons}>
              {taskTypes.map((type) => (
                <button
                  key={type}
                  className={`${styles.filterButton} ${filter === type ? styles.active : ''}`}
                  onClick={() => setFilter(type)}
                >
                  {type.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.workflowGrid}>
            {filteredWorkflows.map((workflow) => (
              <WorkflowCard
                key={workflow.workflow_id}
                workflow={workflow}
                onPurchase={handlePurchase}
                purchased={purchasedIds.has(workflow.workflow_id)}
              />
            ))}
          </div>

          {filteredWorkflows.length === 0 && (
            <div className={styles.emptyState}>
              <p>No workflows found for this filter.</p>
            </div>
          )}
        </div>
      </main>

      {purchasingWorkflow && (
        <PurchaseModal
          workflow={purchasingWorkflow}
          apiBase={API_BASE}
          onClose={() => setPurchasingWorkflow(null)}
          onSuccess={handlePurchaseSuccess}
        />
      )}

      <Footer />
    </>
  )
}
