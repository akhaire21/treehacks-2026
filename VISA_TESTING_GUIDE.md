# 🧪 Visa Payment Testing Guide

Complete guide to test Visa CyberSource and Visa Direct integration.

---

## 📋 Prerequisites

Before testing, you need:
1. ✅ Visa Developer account
2. ✅ Sandbox/test credentials
3. ✅ Backend running on port 5001
4. ✅ Frontend running on port 3000

---

## 🔑 Step 1: Get Visa Sandbox Credentials (10 minutes)

### 1.1 Register on Visa Developer Platform

1. Go to **https://developer.visa.com**
2. Click **"Register"** (top right)
3. Fill in details:
   - Email: your email
   - First/Last name
   - Company: "TreeHacks 2025" or your team name
   - Country: United States

### 1.2 Create a Project

1. After login, click **"Create Project"**
2. Project details:
   - **Name:** `treehacks-marketplace-payments`
   - **Description:** "Payment processing for AI workflow marketplace"

3. **Add APIs** to your project:
   - ✅ **CyberSource** (for payment processing)
   - ✅ **Visa Direct** (for instant payouts)

### 1.3 Get Credentials

1. Go to **Dashboard → Project → Credentials**
2. Copy these values:

```
API Key:        XXXXXXXXXXXXXX
User ID:        merchant_123
Password:       your_password
Shared Secret:  your_shared_secret_key
Merchant ID:    your_merchant_profile_id
```

### 1.4 Add to Backend .env

Edit `backend/.env`:
```bash
# Visa Developer API (Sandbox/Test)
VISA_API_KEY=your-api-key-here
VISA_USER_ID=your-merchant-id
VISA_PASSWORD=your-password
VISA_SHARED_SECRET=your-shared-secret
VISA_MERCHANT_ID=your-merchant-profile-id

# Use SANDBOX endpoints for testing
CYBERSOURCE_URL=https://apitest.cybersource.com
VISA_DIRECT_URL=https://sandbox.api.visa.com/visadirect

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

**Restart backend after adding credentials:**
```bash
./stop-backend.sh
./start-backend.sh
```

---

## 🧪 Step 2: Test API Endpoints

### 2.1 Check Visa Integration Status

```bash
curl http://localhost:5001/api/visa/health
```

**Expected Response:**
```json
{
  "visa_configured": true,
  "cybersource_url": "https://apitest.cybersource.com",
  "visa_direct_url": "https://sandbox.api.visa.com/visadirect"
}
```

If `visa_configured: false`, check your `.env` credentials.

---

## 💳 Step 3: Test Token Purchase (CyberSource)

### 3.1 Create Payment Session

```bash
curl -X POST http://localhost:5001/api/visa/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "token_package": "pro"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "payment_url": "https://apitest.cybersource.com/pay",
  "transaction_id": "txn_1739483927_test_user_123",
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

### 3.2 Test Payment UI

Create a test page: `app/test-visa/page.tsx`

```tsx
'use client'

export default function TestVisaPage() {
  const testPayment = async () => {
    const response = await fetch('http://localhost:5001/api/visa/create-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: 'test_user',
        token_package: 'starter',
      }),
    })

    const result = await response.json()

    if (result.success) {
      // Create form and submit to CyberSource
      const form = document.createElement('form')
      form.method = 'POST'
      form.action = result.payment_url

      Object.entries(result.form_data).forEach(([key, value]) => {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = key
        input.value = value as string
        form.appendChild(input)
      })

      document.body.appendChild(form)
      form.submit()
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Test Visa Payment</h1>
      <button
        onClick={testPayment}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg"
      >
        Test Payment Flow
      </button>
    </div>
  )
}
```

Visit: http://localhost:3000/test-visa

### 3.3 Use Test Card Numbers

When redirected to CyberSource payment page, use these **test cards**:

| Card Number | Type | CVV | Expiry | Result |
|-------------|------|-----|--------|--------|
| `4111111111111111` | Visa | `123` | `12/2025` | ✅ **Success** |
| `4000000000000002` | Visa | `123` | `12/2025` | ❌ Decline |
| `5555555555554444` | Mastercard | `123` | `12/2025` | ✅ Success |
| `378282246310005` | Amex | `1234` | `12/2025` | ✅ Success |

**Billing Info (for test):**
- Name: Test User
- Address: 123 Test St
- City: San Francisco
- State: CA
- ZIP: 94105

### 3.4 Complete Payment

1. Enter test card: `4111111111111111`
2. CVV: `123`
3. Expiry: `12/2025`
4. Click **"Pay Now"**
5. You'll be redirected to success page

**Backend should log:**
```
✅ Visa payment successful: test_user received 1000 tokens ($10.00)
```

---

## 💰 Step 4: Test Creator Payout (Visa Direct)

### 4.1 Test Instant Payout API

```bash
curl -X POST http://localhost:5001/api/visa/payout-creator \
  -H "Content-Type: application/json" \
  -d '{
    "creator_id": "creator_123",
    "card_number": "4111111111111111",
    "amount_tokens": 1700,
    "workflow_id": "ohio_w2_itemized_2024"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "transaction_id": "payout_1739484127_creator_123",
  "status": "approved",
  "approval_code": "888888",
  "amount": 17.0,
  "creator_id": "creator_123",
  "workflow_id": "ohio_w2_itemized_2024",
  "message": "Payout successful - funds pushed to card"
}
```

**Backend should log:**
```
💰 Visa Direct payout: $17.00 to creator creator_123
```

### 4.2 Test Cards for Visa Direct

Use these cards for testing payouts:

| Card Number | Type | Result |
|-------------|------|--------|
| `4111111111111111` | Visa | ✅ Approved |
| `4005550000000019` | Visa | ✅ Approved |
| `4957030420210454` | Visa | ✅ Approved |

---

## 🎯 Step 5: Test Full Purchase Flow

### 5.1 Complete E2E Test

```bash
# 1. User buys tokens
curl -X POST http://localhost:5001/api/visa/create-payment \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "token_package": "pro"}'

# Complete payment in browser with test card

# 2. User buys workflow (2000 tokens)
curl -X POST http://localhost:5001/api/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "ohio_w2_itemized_2024",
    "user_id": "alice"
  }'

# 3. Creator gets paid (1700 tokens = $17)
curl -X POST http://localhost:5001/api/visa/payout-creator \
  -H "Content-Type: application/json" \
  -d '{
    "creator_id": "bob",
    "card_number": "4111111111111111",
    "amount_tokens": 1700,
    "workflow_id": "ohio_w2_itemized_2024"
  }'
```

### 5.2 Expected Flow

```
User Alice:
  Pays $45 via Visa → Gets 5,000 tokens
  Buys workflow for 2,000 tokens
  Remaining: 3,000 tokens

Platform:
  Takes 300 tokens (15% fee) = $3.00

Creator Bob:
  Gets 1,700 tokens = $17.00
  Instant payout via Visa Direct ⚡
```

---

## 📊 Step 6: Monitor & Verify

### 6.1 Check Transaction Logs

**Backend logs:**
```
💳 Payment: alice purchased 5000 tokens for $45.00
✅ Purchase: alice bought ohio_w2_itemized_2024 for 2000 tokens
💰 Payout: Creator bob received $17.00 to card *1111
```

### 6.2 Verify User Balance

```bash
curl http://localhost:5001/api/commerce/balance?user_id=alice
```

**Response:**
```json
{
  "user_id": "alice",
  "balance": 3000
}
```

### 6.3 Check Transaction History

```bash
curl http://localhost:5001/api/commerce/transactions?user_id=alice&limit=10
```

---

## 🐛 Troubleshooting

### Issue: "visa_configured: false"

**Solution:**
```bash
# Check .env file
cat backend/.env | grep VISA

# Make sure all VISA_* variables are set
# Restart backend
./stop-backend.sh
./start-backend.sh
```

### Issue: "Invalid signature"

**Solution:**
- Check `VISA_SHARED_SECRET` is correct
- Ensure no extra spaces in .env values
- Verify credentials from Visa Dashboard

### Issue: Payment redirects but no callback

**Solution:**
```bash
# Check FRONTEND_URL is correct in .env
FRONTEND_URL=http://localhost:3000

# Create success page: app/payment/success/page.tsx
```

### Issue: "Payout failed"

**Solution:**
- Use sandbox URL: `https://sandbox.api.visa.com/visadirect`
- Use test card: `4111111111111111`
- Check `VISA_API_KEY` and `VISA_USER_ID` are correct

### Issue: CORS errors

**Solution:**
Backend already has CORS enabled in `api.py`:
```python
from flask_cors import CORS
CORS(app)
```

If still failing, check browser console and restart backend.

---

## ✅ Testing Checklist

- [ ] Visa Developer account created
- [ ] Sandbox credentials added to backend/.env
- [ ] Backend restarted with Visa enabled
- [ ] `/api/visa/health` returns `visa_configured: true`
- [ ] Payment session created successfully
- [ ] Test payment completes with card `4111111111111111`
- [ ] Tokens credited to user account
- [ ] Workflow purchase works
- [ ] Creator payout via Visa Direct succeeds
- [ ] Transaction logs show all steps

---

## 🎬 Demo for Judges

**Perfect demo flow:**

1. **Show payment UI**: "Users buy tokens with Visa cards"
2. **Use test card**: `4111111111111111`
3. **Payment succeeds**: "5,000 tokens credited instantly"
4. **Buy workflow**: "User purchases AI workflow for 2,000 tokens"
5. **Creator payout**: "Creator receives $17 via Visa Direct in seconds!"
6. **Show logs**: Highlight instant payout (not 2-7 days like competitors)

**Key talking points:**
- ✅ Visa CyberSource for secure payment processing
- ✅ Visa Direct for **instant** creator payouts (game-changer!)
- ✅ 85/15 revenue split handled automatically
- ✅ Full transaction history and auditing

---

## 📚 Additional Resources

- **Visa Developer Docs**: https://developer.visa.com/capabilities/cybersource
- **Test Cards**: https://developer.cybersource.com/hello-world/testing-guide.html
- **Visa Direct API**: https://developer.visa.com/capabilities/visa_direct
- **Integration Guide**: [VISA_INTEGRATION.md](./VISA_INTEGRATION.md)

---

**Ready to test? Start with Step 1 and get your sandbox credentials!** 🚀

**Quick test:** `curl http://localhost:5001/api/visa/health`
