'use client'

import styles from './Nav.module.css'

export default function Nav() {
  return (
    <nav className={styles.nav}>
      <div className={styles.navLogo}>
        mark<span>.ai</span>
      </div>
      <div className={styles.navLinks}>
        <a href="#how">How it works</a>
        <a href="#marketplace">Marketplace</a>
        <a href="#agent">Agent</a>
        <a href="#dashboard">Dashboard</a>
        <a href="#" className={styles.navCta}>
          Get Started
        </a>
      </div>
    </nav>
  )
}
