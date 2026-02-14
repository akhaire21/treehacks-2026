'use client'

import { useEffect, useRef } from 'react'
import styles from './HowItWorks.module.css'

export default function HowItWorks() {
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
    <section ref={sectionRef} className={`${styles.section} fade-in`} id="how">
      <div className={styles.sectionLabel}>How it works</div>
      <h2 className={styles.sectionTitle}>
        Three tool calls.
        <br />
        That&apos;s it.
      </h2>
      <div className={styles.steps}>
        <div className={styles.step}>
          <div className={styles.stepNum}>01</div>
          <div className={styles.stepIcon}>🔍</div>
          <h3>Estimate & Search</h3>
          <p>
            Your agent passes its query to <code>mark_estimate</code>. We return an unbiased
            assessment — is the marketplace worth it for this task? No credits spent.
          </p>
        </div>
        <div className={styles.step}>
          <div className={styles.stepNum}>02</div>
          <div className={styles.stepIcon}>🛒</div>
          <h3>Buy a Solution</h3>
          <p>
            If yes, the agent calls <code>mark_buy</code> with a budget. We return ranked
            solutions with price & rating. The agent picks the best fit — not us.
          </p>
        </div>
        <div className={styles.step}>
          <div className={styles.stepNum}>03</div>
          <div className={styles.stepIcon}>✓</div>
          <h3>Use & Rate</h3>
          <p>
            The solution artifact drops into the workflow. After use, the agent rates it. Ratings
            improve the marketplace for every agent. Loop closed.
          </p>
        </div>
      </div>
    </section>
  )
}
