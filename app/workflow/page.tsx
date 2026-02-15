'use client'

import WorkflowVisualizer from '@/components/WorkflowVisualizer'
import styles from './page.module.css'

export default function WorkflowPage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <a href="/" className={styles.logo}>
          mark<span className={styles.dot}>.</span>
        </a>
        <div className={styles.badge}>workflow explorer</div>
      </header>
      <main className={styles.main}>
        <h1 className={styles.title}>Agent → Marketplace Flow</h1>
        <p className={styles.subtitle}>
          Interactive visualization of how agents query, purchase, and rate solutions through the Mark protocol.
        </p>
        <WorkflowVisualizer />
      </main>
    </div>
  )
}
