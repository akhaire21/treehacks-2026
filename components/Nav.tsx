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
        <a href="#tools">Tools</a>
        <a href="#dashboard">Dashboard</a>
        <a href="https://docs.mark.ai" target="_blank" rel="noopener noreferrer">
          Docs
        </a>
        <UserInfo />
      </div>
    </nav>
  )
}
