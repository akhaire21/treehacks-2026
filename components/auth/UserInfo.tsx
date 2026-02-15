'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { User } from '@supabase/supabase-js'
import LogoutButton from './LogoutButton'
import Link from 'next/link'

export default function UserInfo({ onAuthChange }: { onAuthChange?: (loggedIn: boolean) => void }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const supabase = createClient()
    if (!supabase) {
      setLoading(false)
      return
    }

    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
      onAuthChange?.(!!user)
    }

    getUser()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      onAuthChange?.(!!session?.user)
    })

    return () => subscription.unsubscribe()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  if (!user) {
    return (
      <Link
        href="/auth/login"
        style={{
          padding: '8px 16px',
          backgroundColor: '#000',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: '500'
        }}
      >
        Login
      </Link>
    )
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <Link
        href="/marketplace"
        style={{
          padding: '8px 16px',
          backgroundColor: 'var(--accent)',
          color: 'var(--bg)',
          textDecoration: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: '600'
        }}
      >
        Marketplace
      </Link>
      <span style={{ fontSize: '14px', color: 'var(--text-dim)' }}>
        {user.email}
      </span>
      <LogoutButton />
    </div>
  )
}
