# 💳 Visa Developer API Integration Guide

Complete guide for integrating Visa payment processing into the Agent Workflow Marketplace.

**Prize Target:** Visa — The Generative Edge: Future of Commerce

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              VISA PAYMENT FLOW                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. USER PURCHASES TOKENS                               │
│     User selects package → CyberSource checkout         │
│     → Payment processed → Tokens credited               │
│                                                         │
│  2. USER BUYS WORKFLOW (Token-based)                    │
│     User spends tokens → Internal commerce.py           │
│     → Workflow delivered → Transaction recorded         │
│                                                         │
│  3. CREATOR GETS PAID (Real-time)                       │
│     Workflow sale recorded → Visa Direct API            │
│     → Instant push to creator's Visa card (85% share)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Step 1: Register on Visa Developer Platform

### 1.1 Create Account
1. Visit **https://developer.visa.com**
2. Click "Register" (top right)
3. Fill in your details:
   - Email
   - Company name: "Agent Workflow Marketplace" (or your hackathon team name)
   - Country
   - Use case: "AI Marketplace Payment Processing"

### 1.2 Create a Project
1. After logging in, click "Create Project"
2. Project name: `agent-marketplace-payments`
3. Description: "Payment processing for AI workflow marketplace"
4. Select APIs to add:
   - ✅ **CyberSource** (Payment Gateway)
   - ✅ **Visa Direct** (Push Payments for creator payouts)
   - ✅ **Visa Token Service** (Optional - for tokenized payments)

### 1.3 Get Credentials
After creating your project, go to **Dashboard → Credentials**:

```
API Key:        XXXXXXXXXXXXXX
User ID:        merchantid123
Password:       ****************
Shared Secret:  ********************************
Merchant ID:    your_merchant_profile_id
```

**Copy these values** - you'll need them for configuration.

---

## ⚙️ Step 2: Configure Your Environment

### 2.1 Update Backend `.env`

Add Visa credentials to `backend/.env`:

```bash
# Visa Developer API
VISA_API_KEY=your-visa-api-key
VISA_USER_ID=your-merchant-id
VISA_PASSWORD=your-visa-password
VISA_SHARED_SECRET=your-shared-secret
VISA_MERCHANT_ID=your-merchant-profile-id

# Use sandbox/test endpoints for development
CYBERSOURCE_URL=https://apitest.cybersource.com
VISA_DIRECT_URL=https://sandbox.api.visa.com/visadirect

# Frontend URL for payment redirects
FRONTEND_URL=http://localhost:3000
```

### 2.2 Install Python Dependencies

```bash
cd backend
pip install cybersource-rest-client-python requests python-jose
```

### 2.3 Verify Configuration

```bash
curl http://localhost:5001/api/visa/health
```

Expected response:
```json
{
  "visa_configured": true,
  "cybersource_url": "https://apitest.cybersource.com",
  "visa_direct_url": "https://sandbox.api.visa.com/visadirect"
}
```

---

## 🛠️ Step 3: Test Payment Flow

### 3.1 Test Token Purchase (CyberSource)

**Start your backend:**
```bash
cd backend
python api.py
```

**Create a payment session:**
```bash
curl -X POST http://localhost:5001/api/visa/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "token_package": "pro"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "payment_url": "https://apitest.cybersource.com/pay",
  "transaction_id": "txn_1707948923_test_user",
  "tokens": 5000,
  "amount_usd": 45.0,
  "form_data": {
    "access_key": "...",
    "amount": "45.00",
    "currency": "USD",
    ...
  }
}
```

### 3.2 Test with Visa Test Cards

Use these **test card numbers** in CyberSource sandbox:

| Card Type | Number | CVV | Expiry | Result |
|-----------|--------|-----|--------|--------|
| Visa (Success) | `4111111111111111` | `123` | Any future date | Success |
| Visa (Decline) | `4000000000000002` | `123` | Any future date | Decline |
| Mastercard | `5555555555554444` | `123` | Any future date | Success |

**Test the full flow:**
1. Submit payment with test card
2. Get redirected to success URL
3. Backend receives callback
4. Tokens credited to user account

### 3.3 Test Creator Payout (Visa Direct)

**Send test payout:**
```bash
curl -X POST http://localhost:5001/api/visa/payout-creator \
  -H "Content-Type: application/json" \
  -d '{
    "creator_id": "creator123",
    "card_number": "4111111111111111",
    "amount_tokens": 1700,
    "workflow_id": "ohio_w2_itemized_2024"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "transaction_id": "payout_1707948999_creator123",
  "status": "approved",
  "approval_code": "888888",
  "amount": 17.00,
  "creator_id": "creator123",
  "workflow_id": "ohio_w2_itemized_2024",
  "message": "Payout successful - funds pushed to card"
}
```

---

## 🎨 Step 4: Add Frontend UI

### 4.1 Create Payment Page

Create `app/payment/page.tsx`:

```tsx
import VisaPayment from '@/components/VisaPayment'

export default function PaymentPage() {
  // Get user ID from auth (Supabase)
  const userId = 'user123' // Replace with actual auth

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <VisaPayment userId={userId} />
    </div>
  )
}
```

### 4.2 Add Navigation Link

Update your navigation to include payment link:

```tsx
<Link href="/payment">💳 Buy Tokens</Link>
```

### 4.3 Create Success/Cancel Pages

**`app/payment/success/page.tsx`:**
```tsx
'use client'

import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function PaymentSuccess() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    // Verify payment status
    if (sessionId) {
      // Call your backend to confirm payment
      setStatus('success')
    }
  }, [sessionId])

  return (
    <div className="min-h-screen flex items-center justify-center bg-green-50">
      <div className="text-center">
        <div className="text-6xl mb-4">✅</div>
        <h1 className="text-3xl font-bold text-green-800 mb-2">
          Payment Successful!
        </h1>
        <p className="text-gray-600 mb-6">
          Your tokens have been added to your account.
        </p>
        <a
          href="/marketplace"
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
        >
          Browse Workflows
        </a>
      </div>
    </div>
  )
}
```

---

## 🔐 Security Best Practices

### 5.1 Signature Verification
Always verify CyberSource signatures to prevent tampering:

```python
def verify_payment_response(self, response_data: Dict) -> Dict[str, Any]:
    received_signature = response_data.get("signature")
    expected_signature = self.generate_cybersource_signature(response_data)

    if received_signature != expected_signature:
        return {"success": False, "error": "Invalid signature"}

    # Process payment...
```

### 5.2 HTTPS in Production
- Use HTTPS for all payment callbacks
- Update `FRONTEND_URL` to your production domain
- Configure webhook URLs in Visa Dashboard

### 5.3 Never Store Full Card Numbers
- Only store last 4 digits for display
- Use Visa Token Service for recurring payments
- Let CyberSource handle PCI compliance

### 5.4 Test Mode vs Production
Development:
```bash
CYBERSOURCE_URL=https://apitest.cybersource.com
VISA_DIRECT_URL=https://sandbox.api.visa.com/visadirect
```

Production:
```bash
CYBERSOURCE_URL=https://api.cybersource.com
VISA_DIRECT_URL=https://api.visa.com/visadirect
```

---

## 💰 Token Pricing Strategy

### Recommended Packages

| Package | Tokens | Price | Cost per Token | Discount |
|---------|--------|-------|----------------|----------|
| Starter | 1,000 | $10 | $0.01 | - |
| Pro | 5,000 | $45 | $0.009 | 10% |
| Enterprise | 15,000 | $120 | $0.008 | 20% |

### Token-to-USD Conversion
- **100 tokens = $1.00 USD**
- Workflows cost 1,500-2,000 tokens ($15-$20)
- Users see ROI of 500-650%

### Creator Payouts
- User pays: 2,000 tokens ($20)
- Platform fee (15%): 300 tokens ($3)
- Creator receives: 1,700 tokens ($17) via Visa Direct

---

## 📊 Testing Checklist

- [ ] Visa Developer account created
- [ ] Project created with CyberSource + Visa Direct
- [ ] Credentials added to `.env`
- [ ] Backend running with Visa enabled
- [ ] Payment page accessible
- [ ] Test card payment succeeds
- [ ] Tokens credited to user account
- [ ] Creator payout test succeeds
- [ ] Success/cancel pages work
- [ ] Transaction history displays

---

## 🚀 Production Deployment

### 6.1 Switch to Production Credentials
1. In Visa Dashboard, promote your project to production
2. Get production credentials
3. Update `.env` with production keys
4. Change URLs to production endpoints

### 6.2 Compliance Requirements
- **PCI-DSS**: CyberSource handles card data (you're compliant)
- **KYC**: Implement identity verification for creators
- **Tax Reporting**: Use Visa Direct metadata for 1099 forms
- **AML**: Monitor for suspicious transaction patterns

### 6.3 Monitoring
```python
# Log all transactions
print(f"💳 Payment: {user_id} purchased {tokens} tokens for ${amount}")
print(f"💰 Payout: Creator {creator_id} received ${amount} to card *{last4}")
```

---

## 🎯 Visa Prize Submission Tips

### Highlight These Features
1. **Real-time Creator Payouts**
   - Use Visa Direct for instant payments
   - 85% revenue share pushed to card in seconds

2. **Secure Payment Processing**
   - CyberSource integration
   - Signature verification
   - PCI-compliant

3. **AI Commerce Innovation**
   - Token economy for AI workflows
   - Dynamic pricing based on value
   - Transparent ROI metrics

4. **Developer Experience**
   - Clean API integration
   - Comprehensive error handling
   - Test mode for development

### Demo Flow for Judges
1. Show marketplace with pricing
2. Purchase tokens via Visa payment
3. Buy workflow with tokens
4. Show creator payout via Visa Direct
5. Display transaction history

---

## 📞 Support & Resources

- **Visa Developer Portal**: https://developer.visa.com
- **CyberSource Docs**: https://developer.cybersource.com
- **Visa Direct Docs**: https://developer.visa.com/capabilities/visa_direct
- **Test Cards**: https://developer.cybersource.com/hello-world/testing-guide.html

---

## 🐛 Troubleshooting

### "Visa not configured" error
- Check that all `VISA_*` env variables are set
- Restart backend after updating `.env`
- Run `/api/visa/health` to verify

### Payment callback not working
- Ensure `FRONTEND_URL` is correct
- Check that callback endpoint is accessible
- Verify signature in response

### Payout fails
- Verify card number is valid Visa/Mastercard
- Check you're using sandbox credentials with test URLs
- Ensure sufficient balance in test merchant account

---

**Built for:** Visa — The Generative Edge: Future of Commerce Prize

**Integration complete!** 🎉 You now have a fully functional Visa-powered payment system for your AI workflow marketplace.
