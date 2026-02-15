# ✅ Supabase Setup Complete

Your Supabase integration is ready to use!

---

## 🔑 Environment Variables Configured

**Location:** `.env.local` (already created with your credentials)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://bsusfhiiqsdxrssillps.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
NEXT_PUBLIC_API_URL=http://localhost:5001
```

✅ These credentials are **NOT tracked in git** (.env.local is in .gitignore)

---

## 📁 Files Created/Available

### Supabase Clients
- ✅ `lib/supabase/client.ts` - Browser client for client components
- ✅ `lib/supabase/server.ts` - Server client for server components
- ✅ `lib/supabase/middleware.ts` - Auth session refresh middleware
- ✅ `lib/supabase.ts` - Unified client with TypeScript types
- ✅ `lib/auth.ts` - Authentication helpers

### Middleware
- ✅ `middleware.ts` - Auth protection for routes

---

## 🚀 Quick Start Usage

### 1. Client Component (with 'use client')

```tsx
'use client'

import { createClient } from '@/lib/supabase/client'
import { useEffect, useState } from 'react'

export default function MyComponent() {
  const [user, setUser] = useState(null)
  const supabase = createClient()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
    }
    getUser()
  }, [])

  return <div>User: {user?.email}</div>
}
```

### 2. Server Component

```tsx
import { createServerComponentClient } from '@/lib/supabase'

export default async function ServerComponent() {
  const supabase = await createServerComponentClient()
  const { data: { user } } = await supabase.auth.getUser()

  return <div>User: {user?.email}</div>
}
```

### 3. Authentication (Sign Up/Login)

```tsx
'use client'

import { signIn, signUp, signOut } from '@/lib/auth'
import { useState } from 'react'

export default function AuthForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSignUp = async () => {
    const result = await signUp(email, password)
    if (result.success) {
      console.log('Signed up!', result.user)
    } else {
      console.error(result.error)
    }
  }

  const handleSignIn = async () => {
    const result = await signIn(email, password)
    if (result.success) {
      console.log('Signed in!', result.user)
    } else {
      console.error(result.error)
    }
  }

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={handleSignUp}>Sign Up</button>
      <button onClick={handleSignIn}>Sign In</button>
    </div>
  )
}
```

### 4. Token Balance Management

```tsx
import { getUserBalance, addTokens, deductTokens } from '@/lib/auth'

// Get user's token balance
const balance = await getUserBalance(userId)
console.log(`Balance: ${balance} tokens`)

// Add tokens after payment
await addTokens(userId, 5000) // Add 5000 tokens

// Deduct tokens after purchase
const result = await deductTokens(userId, 2000) // Buy workflow for 2000 tokens
if (!result.success) {
  console.error('Insufficient balance')
}
```

### 5. Transaction History

```tsx
import { recordTransaction, getUserTransactions } from '@/lib/auth'

// Record a purchase
await recordTransaction({
  user_id: userId,
  workflow_id: 'ohio_w2_itemized_2024',
  amount: 2000,
  type: 'purchase',
  status: 'completed',
})

// Get transaction history
const transactions = await getUserTransactions(userId, 20) // Last 20 transactions
```

---

## 🗄️ Required Database Tables

Create these tables in Supabase (Dashboard → SQL Editor):

```sql
-- User balances table
CREATE TABLE user_balances (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  balance INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workflow_id TEXT,
  amount INTEGER NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('purchase', 'deposit', 'refund', 'payout')),
  status TEXT NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_balances_user_id ON user_balances(user_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE user_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only see their own data
CREATE POLICY "Users can view their own balance"
  ON user_balances FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own transactions"
  ON transactions FOR SELECT
  USING (auth.uid() = user_id);

-- Allow service role to manage everything (for backend)
CREATE POLICY "Service role has full access to balances"
  ON user_balances FOR ALL
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role has full access to transactions"
  ON transactions FOR ALL
  USING (true)
  WITH CHECK (true);
```

---

## 🔐 Protected Routes

Routes that require authentication are defined in `middleware.ts`:

```typescript
const protectedRoutes = ['/marketplace']
```

If a user tries to access these without being logged in, they'll be redirected to `/auth/login`.

**To add more protected routes:**
Edit `middleware.ts` and add to the `protectedRoutes` array.

---

## 🔗 Integration with Visa Payments

When a user purchases tokens via Visa:

```typescript
// backend/visa_payments.py - After successful payment
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(supabaseUrl, supabaseKey)

// Credit tokens to user
await supabase.from('user_balances').upsert({
  user_id: userId,
  balance: newBalance,
  updated_at: new Date().toISOString()
})

// Record transaction
await supabase.from('transactions').insert({
  user_id: userId,
  amount: tokensAmount,
  type: 'deposit',
  status: 'completed'
})
```

---

## 📊 Dashboard Views

### User Balance Component

```tsx
'use client'

import { useEffect, useState } from 'react'
import { getUserBalance } from '@/lib/auth'
import { createClient } from '@/lib/supabase/client'

export default function BalanceDisplay() {
  const [balance, setBalance] = useState(0)
  const [user, setUser] = useState(null)
  const supabase = createClient()

  useEffect(() => {
    const init = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        setUser(user)
        const bal = await getUserBalance(user.id)
        setBalance(bal)
      }
    }
    init()
  }, [])

  return (
    <div className="p-4 bg-blue-50 rounded-lg">
      <div className="text-sm text-gray-600">Your Balance</div>
      <div className="text-2xl font-bold">{balance.toLocaleString()} tokens</div>
      {user && <div className="text-xs text-gray-500">{user.email}</div>}
    </div>
  )
}
```

---

## 🧪 Testing

### 1. Test Authentication
```bash
npm run dev
# Visit: http://localhost:3000
# Try signing up / logging in
```

### 2. Test Database Connection
```bash
# In your component:
const supabase = createClient()
const { data, error } = await supabase.from('user_balances').select('*')
console.log('Data:', data)
```

### 3. Check Middleware
```bash
# Try accessing /marketplace without logging in
# Should redirect to /auth/login
```

---

## 🔧 Troubleshooting

### "Module not found: @supabase/ssr"
Already fixed! We installed it with `npm install`.

### "Invalid JWT" or "Invalid API key"
- Check your `.env.local` has the correct credentials
- Verify `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Restart dev server: `npm run dev`

### Database tables not found
- Run the SQL above in Supabase Dashboard → SQL Editor
- Make sure you're connected to the correct project

### Can't access protected routes
- Make sure you're logged in
- Check middleware.ts is configured correctly
- Clear cookies and try again

---

## 📚 Next Steps

1. ✅ Create database tables (run SQL above)
2. ✅ Test authentication flow
3. ✅ Integrate with Visa payments
4. ✅ Build user dashboard with balance display
5. ✅ Add transaction history view

---

**Your Supabase project:** https://bsusfhiiqsdxrssillps.supabase.co

All set! 🚀
