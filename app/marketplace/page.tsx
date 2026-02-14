'use client'

import { useEffect, useState } from 'react'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'
import WorkflowCard from '@/components/WorkflowCard'
import styles from './marketplace.module.css'

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
  avg_tokens_without?: number
  avg_tokens_with?: number
}

export default function MarketplacePage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/workflows')
      if (!response.ok) {
        throw new Error('Failed to fetch workflows')
      }
      const data = await response.json()
      setWorkflows(data.workflows)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = (workflowId: string) => {
    // In a real app, this would handle the purchase flow
    alert(`Purchasing workflow: ${workflowId}`)
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
      <Footer />
    </>
  )
}
