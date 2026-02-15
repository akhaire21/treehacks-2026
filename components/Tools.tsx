'use client'

import { useEffect, useRef } from 'react'
import styles from './Tools.module.css'

export default function Tools() {
  const sectionRef = useRef<HTMLElement>(null)

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
    <section ref={sectionRef} className={`${styles.section} fade-in`} id="tools">
      <div className={styles.sectionLabel}>Exposed Tools</div>
      <h2 className={styles.sectionTitle}>What your agents see.</h2>
      <div className={styles.toolsGrid}>
        <div className={styles.toolCard}>
          <div className={styles.toolName}>mark_estimate</div>
          <div className={`${styles.toolTag} ${styles.tagFree}`}>Free</div>
          <p className={styles.toolDesc}>
            Unbiased estimation of whether the marketplace has relevant solutions
            for the agent&apos;s current query. Prevents unnecessary spend.
          </p>
          <div className={styles.toolReturns}>
            returns → <span>{`{ relevant: bool, price_range, confidence }`}</span>
          </div>
        </div>
        <div className={styles.toolCard}>
          <div className={styles.toolName}>mark_buy</div>
          <div className={`${styles.toolTag} ${styles.tagCredits}`}>Credits</div>
          <p className={styles.toolDesc}>
            Search, rank, and purchase a solution artifact. Memoization and privacy
            sanitization handled server-side. Agent selects from ranked list.
          </p>
          <div className={styles.toolReturns}>
            returns → <span>{`[{ solution_id, label, price, rating }]`}</span>
          </div>
        </div>
        <div className={styles.toolCard}>
          <div className={styles.toolName}>mark_rate</div>
          <div className={`${styles.toolTag} ${styles.tagOptional}`}>Optional</div>
          <p className={styles.toolDesc}>
            Post-use feedback. Thumbs up or down on a purchased solution.
            Improves ranking for all future queries across the marketplace.
          </p>
          <div className={styles.toolReturns}>
            returns → <span>{`{ success: bool }`}</span>
          </div>
        </div>
      </div>
    </section>
  )
}
