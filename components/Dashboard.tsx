'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import styles from './Dashboard.module.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

interface Transaction {
  id: string
  workflow_id: string
  buyer_id: string
  amount: number
  timestamp: string
  type: string
}

interface MarketStats {
  total_transactions: number
  total_volume_tokens: number
  unique_buyers: number
  unique_workflows_sold: number
  platform_revenue: number
}

interface TokenPackage {
  id: string
  name: string
  tokens: string
  price: string
  priceValue: number
  discount?: string
  popular?: boolean
  workflows: string
}

const TOKEN_PACKAGES: TokenPackage[] = [
  {
    id: 'starter',
    name: 'Starter',
    tokens: '1,000',
    price: '$10',
    priceValue: 10,
    workflows: '2-3 workflow purchases',
  },
  {
    id: 'pro',
    name: 'Professional',
    tokens: '5,000',
    price: '$45',
    priceValue: 45,
    discount: 'Save 10%',
    popular: true,
    workflows: '10-12 workflow purchases',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    tokens: '15,000',
    price: '$120',
    priceValue: 120,
    discount: 'Save 20%',
    workflows: '30+ workflow purchases',
  },
]

export default function Dashboard() {
  const sectionRef = useRef<HTMLElement>(null)
  const [activeTab, setActiveTab] = useState('Overview')
  const [balance, setBalance] = useState<number | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [stats, setStats] = useState<MarketStats | null>(null)
  const [workflowCount, setWorkflowCount] = useState(0)
  const [cartCount, setCartCount] = useState(0)
  const [live, setLive] = useState(false)
  const [purchaseLoading, setPurchaseLoading] = useState<string | null>(null)
  const [selectedTier, setSelectedTier] = useState<string>('pro')

  const fetchData = useCallback(async () => {
    try {
      const [balRes, txRes, statsRes, wfRes, cartRes] = await Promise.all([
        fetch(`${API}/api/commerce/balance?user_id=default_user`),
        fetch(`${API}/api/commerce/transactions?user_id=default_user&limit=10`),
        fetch(`${API}/api/commerce/stats`),
        fetch(`${API}/api/workflows`),
        fetch(`${API}/api/commerce/cart?user_id=default_user`),
      ])
      const [balData, txData, statsData, wfData, cartData] = await Promise.all([
        balRes.json(), txRes.json(), statsRes.json(), wfRes.json(), cartRes.json(),
      ])
      setBalance(balData.balance)
      setTransactions(txData.transactions || [])
      setStats(statsData)
      setWorkflowCount(wfData.count || 0)
      setCartCount(cartData.item_count || 0)
      setLive(true)
    } catch {
      setLive(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 8000) // Auto-refresh every 8s
    return () => clearInterval(interval)
  }, [fetchData])

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

  const handlePurchase = async (packageId: string) => {
    setPurchaseLoading(packageId)
    try {
      const response = await fetch(`${API}/api/visa/create-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default_user',
          token_package: packageId,
        }),
      })
      const result = await response.json()
      if (!result.success) {
        throw new Error(result.error || 'Failed to create payment session')
      }
      const form = document.createElement('form')
      form.method = 'POST'
      form.action = result.payment_url
      Object.entries(result.form_data).forEach(([key, value]) => {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = key
        input.value = value as string
        form.appendChild(input)
      })
      document.body.appendChild(form)
      form.submit()
    } catch (error) {
      console.error('Payment error:', error)
      alert(`Payment failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setPurchaseLoading(null)
    }
  }

  const volumeStr = stats ? stats.total_volume_tokens.toLocaleString() : '—'
  const balanceStr = balance !== null ? balance.toLocaleString() : '—'

  return (
    <section ref={sectionRef} className={`${styles.dashboardSection} fade-in`} id="dashboard">
      <div className={styles.dashboardContainer}>
        <div className={styles.sectionLabel}>
          Live Dashboard {live && <span style={{ color: 'var(--green)' }}>● connected</span>}
        </div>
        <h2 className={styles.sectionTitle}>
          Full visibility.
          <br />
          Total control.
        </h2>
        <div className={styles.dashboard}>
          <div className={styles.dashHeader}>
            <div className={styles.dashTabs}>
              {['Overview', 'Transactions', 'Agents', 'Wallet', 'Settings'].map((tab) => (
                <button
                  key={tab}
                  className={`${styles.dashTab} ${activeTab === tab ? styles.active : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className={styles.dashWallet}>
              <span className={styles.walletBalance}>◈ {balanceStr} credits</span>
            </div>
          </div>
          <div className={styles.dashBody}>
            <div className={styles.dashSidebar}>
              {[
                { icon: '◉', label: 'Overview' },
                { icon: '↗', label: 'Transactions' },
                { icon: '⬡', label: 'Agents' },
                { icon: '◈', label: 'Wallet' },
                { icon: '⚙', label: 'Settings' },
              ].map(({ icon, label }) => (
                <div
                  key={label}
                  className={`${styles.dashNavItem} ${activeTab === label ? styles.active : ''}`}
                  onClick={() => setActiveTab(label)}
                  style={{ cursor: 'pointer' }}
                >
                  <span className={styles.dashNavIcon}>{icon}</span> {label}
                </div>
              ))}
            </div>
            <div className={styles.dashContent}>
              {activeTab === 'Overview' && (
                <>
                  <div className={styles.dashStats}>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Workflows Available</div>
                      <div className={styles.statValue}>{workflowCount}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>Live from Elasticsearch</div>
                    </div>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Credits Balance</div>
                      <div className={styles.statValue}>{balanceStr}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>
                        Token economy active
                      </div>
                    </div>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Total Transactions</div>
                      <div className={styles.statValue}>{stats?.total_transactions ?? '—'}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>
                        Volume: ◈ {volumeStr}
                      </div>
                    </div>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Cart Items</div>
                      <div className={styles.statValue}>{cartCount}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>
                        {stats?.unique_workflows_sold ?? 0} workflows sold
                      </div>
                    </div>
                  </div>

                  <div className={styles.chartArea}>
                    <div className={styles.chartTitle}>Platform revenue — real-time</div>
                    {[30, 45, 35, 60, 52, 48, 70, 65, 80, 72, 85, 78, 92, 100].map((height, i) => (
                      <div key={i} className={styles.chartBar} style={{ height: `${height}%` }}></div>
                    ))}
                  </div>
                </>
              )}

              {activeTab === 'Transactions' && (
                <table className={styles.txTable}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Workflow</th>
                      <th>Buyer</th>
                      <th>Cost</th>
                      <th>Type</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.length === 0 ? (
                      <tr>
                        <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                          No transactions yet — search &amp; purchase workflows above to see live data
                        </td>
                      </tr>
                    ) : (
                      transactions.map((tx) => (
                        <tr key={tx.id}>
                          <td className={styles.txId}>{tx.id.slice(0, 12)}…</td>
                          <td className={styles.txSolution}>{tx.workflow_id}</td>
                          <td>{tx.buyer_id}</td>
                          <td className={styles.txPrice}>◈ {tx.amount}</td>
                          <td>
                            <span className={`${styles.txRating} ${styles.ratingUp}`}>
                              {tx.type || 'purchase'}
                            </span>
                          </td>
                          <td>
                            <span className={`${styles.txStatus} ${styles.statusComplete}`}>
                              Complete
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              )}

              {activeTab === 'Agents' && (
                <div className={styles.dashStats}>
                  <div className={styles.statCard}>
                    <div className={styles.statLabel}>Unique Buyers</div>
                    <div className={styles.statValue}>{stats?.unique_buyers ?? '—'}</div>
                    <div className={`${styles.statChange} ${styles.statUp}`}>Active agents</div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statLabel}>Workflows Sold</div>
                    <div className={styles.statValue}>{stats?.unique_workflows_sold ?? '—'}</div>
                    <div className={`${styles.statChange} ${styles.statUp}`}>Unique workflows</div>
                  </div>
                </div>
              )}

              {activeTab === 'Wallet' && (
                <>
                  <div className={styles.dashStats}>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Credits Balance</div>
                      <div className={styles.statValue}>{balanceStr}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>
                        Token economy active
                      </div>
                    </div>
                    <div className={styles.statCard}>
                      <div className={styles.statLabel}>Total Volume</div>
                      <div className={styles.statValue}>◈ {volumeStr}</div>
                      <div className={`${styles.statChange} ${styles.statUp}`}>
                        All-time token volume
                      </div>
                    </div>
                  </div>

                  <div className={styles.tierSection}>
                    <div className={styles.tierHeader}>Purchase Tokens</div>
                    <div className={styles.tierSubheader}>Secure payment powered by <span style={{ color: 'var(--accent)' }}>Visa</span></div>
                    <div className={styles.tierGrid}>
                      {TOKEN_PACKAGES.map((pkg) => (
                        <div
                          key={pkg.id}
                          className={`${styles.tierCard} ${selectedTier === pkg.id ? styles.tierSelected : ''} ${pkg.popular ? styles.tierPopular : ''}`}
                          onClick={() => setSelectedTier(pkg.id)}
                        >
                          {pkg.popular && (
                            <div className={styles.tierBadge}>MOST POPULAR</div>
                          )}
                          <div className={styles.tierName}>{pkg.name}</div>
                          <div className={styles.tierTokens}>{pkg.tokens}</div>
                          <div className={styles.tierTokensLabel}>tokens</div>
                          <div className={styles.tierPrice}>{pkg.price}</div>
                          {pkg.discount && (
                            <div className={styles.tierDiscount}>{pkg.discount}</div>
                          )}
                          <div className={styles.tierWorkflows}>{pkg.workflows}</div>
                          <button
                            className={`${styles.tierBtn} ${pkg.popular ? styles.tierBtnPopular : ''}`}
                            onClick={(e) => { e.stopPropagation(); handlePurchase(pkg.id) }}
                            disabled={purchaseLoading === pkg.id}
                          >
                            {purchaseLoading === pkg.id ? 'Processing...' : `Purchase ${pkg.name}`}
                          </button>
                          <div className={styles.tierFeatures}>
                            <div className={styles.tierFeature}>✓ Instant activation</div>
                            <div className={styles.tierFeature}>✓ No expiration</div>
                            <div className={styles.tierFeature}>✓ Secure via Visa</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'Settings' && (
                <div style={{ padding: '24px', color: 'var(--text-muted)' }}>
                  Settings panel — configure API keys, notification preferences, and agent permissions.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}