'use client'

import styles from './Nav.module.css'
import UserInfo from './auth/UserInfo'
import Link from 'next/link'

export default function Nav() {
  return (
    <nav className={styles.nav}>
      <Link href="/" className={styles.navLogo}>
        mark<span>.ai</span>
      </Link>
      <div className={styles.navLinks}>
        <a href="#how">How it works</a>
        <a href="#marketplace">Marketplace</a>
        <a href="#agent">Agent</a>
        <Link href="/sdk">SDK</Link>
        <Link href="/docs">Docs</Link>
        <Link href="/dashboard">Dashboard</Link>
        <a href="/workflow">Visualization</a>
        <UserInfo />
        <Link href="/auth/signup" className={styles.navCta}>
          Get Started
        </Link>
      </div>
    </nav>
  )
}
