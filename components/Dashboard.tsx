'use client'

import { useEffect, useRef, useState } from 'react'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const sectionRef = useRef<HTMLElement>(null)
  const [activeTab, setActiveTab] = useState('Overview')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')
          }
        })
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <section ref={sectionRef} className={`${styles.dashboardSection} fade-in`} id="dashboard">
      <div className={styles.dashboardContainer}>
        <div className={styles.sectionLabel}>Your Dashboard</div>
        <h2 className={styles.sectionTitle}>
          Full visibility.
          <br />
          Total control.
        </h2>
        <div className={styles.dashboard}>
          <div className={styles.dashHeader}>
            <div className={styles.dashTabs}>
              {['Overview', 'Transactions', 'Agents', 'Settings'].map((tab) => (
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
              <span className={styles.walletBalance}>◈ 4,280 credits</span>
            </div>
          </div>
          <div className={styles.dashBody}>
            <div className={styles.dashSidebar}>
              <div className={`${styles.dashNavItem} ${styles.active}`}>
                <span className={styles.dashNavIcon}>◉</span> Overview
              </div>
              <div className={styles.dashNavItem}>
                <span className={styles.dashNavIcon}>↗</span> Transactions
              </div>
              <div className={styles.dashNavItem}>
                <span className={styles.dashNavIcon}>⬡</span> Agents
              </div>
              <div className={styles.dashNavItem}>
                <span className={styles.dashNavIcon}>◈</span> Wallet
              </div>
              <div className={styles.dashNavItem}>
                <span className={styles.dashNavIcon}>⚙</span> Settings
              </div>
            </div>
            <div className={styles.dashContent}>
              <div className={styles.dashStats}>
                <div className={styles.statCard}>
                  <div className={styles.statLabel}>Total Calls</div>
                  <div className={styles.statValue}>12,847</div>
                  <div className={`${styles.statChange} ${styles.statUp}`}>↑ 23% this week</div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statLabel}>Credits Spent</div>
                  <div className={styles.statValue}>1,720</div>
                  <div className={`${styles.statChange} ${styles.statDown}`}>
                    ↓ 8% vs last week
                  </div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statLabel}>Solutions Bought</div>
                  <div className={styles.statValue}>342</div>
                  <div className={`${styles.statChange} ${styles.statUp}`}>↑ 15% this week</div>
                </div>
                <div className={styles.statCard}>
                  <div className={styles.statLabel}>Avg Rating Given</div>
                  <div className={styles.statValue}>4.6</div>
                  <div className={`${styles.statChange} ${styles.statUp}`}>↑ 0.2 pts</div>
                </div>
              </div>

              <div className={styles.chartArea}>
                <div className={styles.chartTitle}>Tool calls — last 14 days</div>
                {[30, 45, 35, 60, 52, 48, 70, 65, 80, 72, 85, 78, 92, 100].map((height, i) => (
                  <div key={i} className={styles.chartBar} style={{ height: `${height}%` }}></div>
                ))}
              </div>

              <table className={styles.txTable}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Solution</th>
                    <th>Agent</th>
                    <th>Cost</th>
                    <th>Rating</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className={styles.txId}>tx_8f2a…c1</td>
                    <td className={styles.txSolution}>Code Review — Rust unsafe blocks</td>
                    <td>ci-agent-03</td>
                    <td className={styles.txPrice}>◈ 12</td>
                    <td>
                      <span className={`${styles.txRating} ${styles.ratingUp}`}>▲ up</span>
                    </td>
                    <td>
                      <span className={`${styles.txStatus} ${styles.statusComplete}`}>
                        Complete
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className={styles.txId}>tx_3e91…d7</td>
                    <td className={styles.txSolution}>Legal clause extraction — NDA</td>
                    <td>doc-parser</td>
                    <td className={styles.txPrice}>◈ 28</td>
                    <td>
                      <span className={`${styles.txRating} ${styles.ratingUp}`}>▲ up</span>
                    </td>
                    <td>
                      <span className={`${styles.txStatus} ${styles.statusComplete}`}>
                        Complete
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className={styles.txId}>tx_7b44…a3</td>
                    <td className={styles.txSolution}>Image captioning — product photos</td>
                    <td>content-gen</td>
                    <td className={styles.txPrice}>◈ 8</td>
                    <td>
                      <span className={`${styles.txRating} ${styles.ratingDown}`}>▼ down</span>
                    </td>
                    <td>
                      <span className={`${styles.txStatus} ${styles.statusComplete}`}>
                        Complete
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className={styles.txId}>tx_1dc8…f5</td>
                    <td className={styles.txSolution}>SQL optimization — join rewrite</td>
                    <td>db-agent</td>
                    <td className={styles.txPrice}>◈ 15</td>
                    <td>
                      <span className={`${styles.txRating} ${styles.ratingUp}`}>▲ up</span>
                    </td>
                    <td>
                      <span className={`${styles.txStatus} ${styles.statusPending}`}>Pending</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
