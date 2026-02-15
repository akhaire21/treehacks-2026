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
    return null
  }

  if (!user) {
    return (
      <Link
        href="/auth/login"
        style={{
          padding: '6px 16px',
          color: 'var(--text-dim)',
          textDecoration: 'none',
          fontSize: '13px',
          fontWeight: '500',
          letterSpacing: '0.5px',
          textTransform: 'uppercase' as const,
          transition: 'color 0.2s',
        }}
      >
        Login
      </Link>
    )
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <span style={{ fontSize: '12px', color: 'var(--text-muted)', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {user.email}
      </span>
      <LogoutButton />
    </div>
  )
}
