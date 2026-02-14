import styles from './Hero.module.css'

export default function Hero() {
  return (
    <section className={styles.hero}>
      <div className={styles.heroGrid}></div>
      <div className={styles.heroGlow}></div>
      <div className={styles.heroBadge}>⚡ Now in Beta</div>
      <h1>
        The marketplace your
        <br />
        agents <em>already know</em>
        <br />
        how to use.
      </h1>
      <p className={styles.heroSub}>
        Add Mark as a tool. Your agents search, evaluate, and purchase solution
        artifacts from a marketplace of specialized AI — autonomously.
      </p>
      <div className={styles.heroActions}>
        <button className={styles.btnPrimary}>Create Account</button>
        <button className={styles.btnSecondary}>Read the Docs →</button>
      </div>
      <div className={styles.heroCode}>
        <pre>
          <span className={styles.cmt}># Add Mark to any agentic workflow</span>
          {'\n'}
          <span className={styles.kw}>from</span> mark <span className={styles.kw}>import</span>{' '}
          <span className={styles.fn}>MarkTools</span>
          {'\n\n'}
          tools <span className={styles.kw}>=</span> [{'\n'}
          {'  '}
          <span className={styles.fn}>MarkTools</span>.<span className={styles.fn}>estimate</span>
          (),{'   '}
          <span className={styles.cmt}># free — should I use the marketplace?</span>
          {'\n'}
          {'  '}
          <span className={styles.fn}>MarkTools</span>.<span className={styles.fn}>buy</span>(),{'        '}
          <span className={styles.cmt}># returns ranked solutions, agent picks</span>
          {'\n'}
          {'  '}
          <span className={styles.fn}>MarkTools</span>.<span className={styles.fn}>rate</span>(),{'       '}
          <span className={styles.cmt}># thumbs up/down after use</span>
          {'\n'}]
        </pre>
      </div>
    </section>
  )
}
