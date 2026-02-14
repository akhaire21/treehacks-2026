'use client'

import { useEffect, useRef, useState } from 'react'
import styles from './Marketplace.module.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

interface WorkflowResult {
  workflow_id: string
  match_percentage: number
  task_type?: string
  description?: string
  rating?: number
  usage_count?: number
  token_cost?: number
  steps?: any[]
}

const QUICK_SEARCHES = [
  { label: 'Ohio tax filing', query: { task_type: 'tax_filing', state: 'ohio' } },
  { label: 'Grocery optimizer', query: { task_type: 'shopping' } },
  { label: 'PDF medical parser', query: { task_type: 'document_parsing' } },
  { label: 'Travel planning', query: { task_type: 'travel_planning' } },
  { label: 'Electronics advisor', query: { task_type: 'product_comparison' } },
  { label: 'Subscription audit', query: { task_type: 'finance_optimization' } },
]

export default function Marketplace() {
  const sectionRef = useRef<HTMLElement>(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<WorkflowResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [toast, setToast] = useState<string | null>(null)
  const [purchasedIds, setPurchasedIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.1 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => {
      if (sectionRef.current) observer.unobserve(sectionRef.current)
    }
  }, [])

  const search = async (searchQuery?: Record<string, any>) => {
    setLoading(true)
    setSearched(true)
    try {
      const body = searchQuery || { task_type: query }
      const res = await fetch(`${API}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      setResults(data.results || [])
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const purchase = async (workflowId: string) => {
    try {
      const res = await fetch(`${API}/api/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_id: workflowId, user_id: 'default_user' }),
      })
      const data = await res.json()
      if (data.success) {
        setPurchasedIds((prev) => new Set(prev).add(workflowId))
        showToast(`Purchased ${workflowId} for ${data.receipt?.amount || '?'} tokens`)
      }
    } catch {
      showToast('Purchase failed — check backend')
    }
  }

  const addToCart = async (workflowId: string) => {
    try {
      await fetch(`${API}/api/commerce/cart/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_id: workflowId, user_id: 'default_user' }),
      })
      showToast(`Added ${workflowId} to cart`)
    } catch {
      showToast('Failed to add to cart')
    }
  }

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <section ref={sectionRef} className={`${styles.section} fade-in`} id="marketplace">
      <div className={styles.container}>
        <div className={styles.sectionLabel}>Live Marketplace</div>
        <h2 className={styles.sectionTitle}>
          Hybrid search.
          <br />
          Real results.
        </h2>
        <p className={styles.sectionSub}>
          Every search hits Elasticsearch Cloud with JINA v3 embeddings for semantic kNN
          similarity + BM25 text matching. Try it live.
        </p>

        <div className={styles.searchBox}>
          <div className={styles.searchHeader}>
            <span className={styles.searchLabel}>Elasticsearch + JINA</span>
            <span className={styles.searchMode}>kNN dense_vector (1024d) + BM25 hybrid</span>
          </div>

          <div className={styles.inputRow}>
            <input
              className={styles.searchInput}
              type="text"
              placeholder="Search workflows... e.g. tax filing, grocery shopping, PDF parsing"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && search()}
            />
            <button
              className={styles.searchBtn}
              onClick={() => search()}
              disabled={loading || !query.trim()}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className={styles.quickTags}>
            {QUICK_SEARCHES.map((qs, i) => (
              <button
                key={i}
                className={styles.quickTag}
                onClick={() => {
                  setQuery(qs.label)
                  search(qs.query)
                }}
              >
                {qs.label}
              </button>
            ))}
          </div>

          {/* Results */}
          {loading && (
            <div className={styles.emptyState}>
              <div className={styles.spinner} />
              Querying Elasticsearch Cloud...
            </div>
          )}

          {!loading && searched && results.length === 0 && (
            <div className={styles.emptyState}>No workflows found. Try a different query.</div>
          )}

          {!loading && results.length > 0 && (
            <div className={styles.results}>
              <div className={styles.resultCount}>
                {results.length} workflow{results.length !== 1 ? 's' : ''} found
              </div>
              {results.map((r, i) => (
                <div key={r.workflow_id} className={styles.resultCard} style={{ animationDelay: `${i * 0.05}s` }}>
                  <div className={styles.resultTop}>
                    <span className={styles.resultName}>{r.workflow_id}</span>
                    <span className={styles.resultMatch}>{r.match_percentage}% match</span>
                  </div>
                  {r.description && <div className={styles.resultDesc}>{r.description}</div>}
                  <div className={styles.resultMeta}>
                    <span className={styles.metaItem}>
                      type <span className={styles.metaVal}>{r.task_type || '—'}</span>
                    </span>
                    <span className={styles.metaItem}>
                      rating <span className={styles.metaVal}>★ {r.rating || '—'}</span>
                    </span>
                    <span className={styles.metaItem}>
                      uses <span className={styles.metaVal}>{r.usage_count || 0}</span>
                    </span>
                    <span className={styles.metaItem}>
                      cost{' '}
                      <span className={`${styles.metaVal} ${styles.metaAccent}`}>
                        ◈ {r.token_cost || '—'}
                      </span>
                    </span>
                    <span className={styles.metaItem}>
                      steps <span className={styles.metaVal}>{r.steps?.length || '—'}</span>
                    </span>
                  </div>
                  <div className={styles.resultActions}>
                    <button
                      className={`${styles.actionBtn} ${styles.buyBtn}`}
                      onClick={() => purchase(r.workflow_id)}
                      disabled={purchasedIds.has(r.workflow_id)}
                    >
                      {purchasedIds.has(r.workflow_id) ? '✓ Purchased' : 'Buy Now'}
                    </button>
                    <button
                      className={`${styles.actionBtn} ${styles.cartBtn}`}
                      onClick={() => addToCart(r.workflow_id)}
                    >
                      + Add to Cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div className={styles.toast}>
          <span className={styles.toastIcon}>✓</span>
          <div>
            <div className={styles.toastText}>{toast}</div>
          </div>
        </div>
      )}
    </section>
  )
}
