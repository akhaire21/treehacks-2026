


import styles from './Hero.module.css'
import Link from 'next/link'

export default function Hero() {
  return (
    <section className={styles.hero}>
      <div className={styles.heroGrid}></div>
      <div className={styles.heroGlow}></div>
      <div className={styles.heroBadge}>⚡ TreeHacks 2026 — Live Demo</div>
      <h1>
        The marketplace your
        <br />
        agents <em>already know</em>
        <br />
        how to use.
      </h1>
      <p className={styles.heroSub}>
        <code style={{ background: 'rgba(0,255,136,0.1)', padding: '2px 8px', borderRadius: '4px', color: '#00ff88', marginRight: '8px' }}>pip install marktools</code>
        {' '}Your agents search, evaluate, and purchase solution
        artifacts from a marketplace of specialized AI — autonomously.
      </p>
      <div className={styles.heroActions}>
        <Link href="/auth/signup" className={styles.btnPrimary} style={{ textDecoration: 'none' }}>Create Account</Link>
        <a href="#agent" className={styles.btnSecondary} style={{ textDecoration: 'none' }}>Try the Live Agent ↓</a>
        <a href="#marketplace" className={styles.btnSecondary} style={{ textDecoration: 'none' }}>Search Marketplace ↓</a>
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
