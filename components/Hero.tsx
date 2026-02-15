'use client'

import styles from './Hero.module.css'
import Link from 'next/link'
import { useState } from 'react'

export default function Hero() {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText('pip install marktools')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <section className={styles.hero}>
      <div className={styles.heroGlow}></div>
      <div className={styles.heroBadge}>⚡ TreeHacks 2026 — Live Demo</div>
      <h1>
        The marketplace your
        <br />
        agents <em>already know</em>
        <br />
        how to use.
      </h1>
      <div className={styles.installBar}>
        <div className={styles.installLabel}>Get MarkTools <span className={styles.installChevron}>&#8964;</span></div>
        <div className={styles.installCommand}>
          <code><span className={styles.installCmd}>pip</span> <span className={styles.installFlag}>install</span> <span className={styles.installPkg}>marktools</span></code>
          <button className={styles.installCopy} onClick={handleCopy} aria-label="Copy command">
            {copied ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
            )}
          </button>
        </div>
      </div>
      <div className={styles.heroActions}>
        <Link href="/auth/signup" className={styles.btnPrimary} style={{ textDecoration: 'none' }}>Create Account</Link>
        <Link href="/marketplace" className={styles.btnSecondary} style={{ textDecoration: 'none' }}>Browse Marketplace →</Link>
        <a href="#marketplace" className={styles.btnSecondary} style={{ textDecoration: 'none' }}>Search Workflows ↓</a>
      </div>
      <div className={styles.heroCode}>
        <pre>
          <span className={styles.cmt}># pip install marktools</span>
          {'\n'}
          <span className={styles.kw}>from</span> marktools <span className={styles.kw}>import</span>{' '}
          <span className={styles.fn}>MarkTools</span>
          {'\n\n'}
          <span className={styles.cmt}># Drop into any agent framework</span>
          {'\n'}
          tools <span className={styles.kw}>=</span>{' '}
          <span className={styles.fn}>MarkTools</span>(api_key=<span className={styles.str}>&quot;mk_...&quot;</span>)
          {'\n\n'}
          <span className={styles.cmt}># Claude</span>
          {'\n'}
          response <span className={styles.kw}>=</span> client.messages.create({'\n'}
          {'  '}tools<span className={styles.kw}>=</span>tools.<span className={styles.fn}>to_anthropic</span>(),{'\n'}
          {'  '}messages<span className={styles.kw}>=</span>[...]{'\n'}
          )
          {'\n\n'}
          <span className={styles.cmt}># Execute tool calls automatically</span>
          {'\n'}
          result <span className={styles.kw}>=</span> tools.<span className={styles.fn}>execute</span>(
          block.name, block.input)
        </pre>
      </div>
    </section>
  )
}
