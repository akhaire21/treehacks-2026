'use client'

import { useState } from 'react'
import styles from './Nav.module.css'
import UserInfo from './auth/UserInfo'
import Link from 'next/link'

export default function Nav() {
  const [loggedIn, setLoggedIn] = useState(false)

  return (
    <nav className={styles.nav}>
      <Link href="/" className={styles.navLogo}>
        mark<span>.ai</span>
      </Link>
      <div className={styles.navLinks}>
        <a href="#agent">Agent</a>
        <Link href="/sdk">SDK</Link>
        <Link href="/docs">Docs</Link>
        <Link href="/dashboard">Dashboard</Link>
        <a href="/workflow">Visualization</a>
        <UserInfo onAuthChange={setLoggedIn} />
        {!loggedIn && (
          <Link href="/auth/signup" className={styles.navCta}>
            Get Started
          </Link>
        )}
      </div>
    </nav>
  )
}
