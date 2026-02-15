# 🚀 Visa Payment Integration - Quick Start

Get Visa payments running in **under 30 minutes**.

---

## ⚡ Quick Setup (5 Steps)

### Step 1: Get Visa Credentials (10 min)
1. Go to **https://developer.visa.com** → Register
2. Create Project → Add **CyberSource** + **Visa Direct**
3. Copy credentials from Dashboard

### Step 2: Configure Backend (5 min)
```bash
cd backend

# Add to .env:
VISA_API_KEY=your-visa-api-key
VISA_USER_ID=your-merchant-id
VISA_PASSWORD=your-visa-password
VISA_SHARED_SECRET=your-shared-secret
VISA_MERCHANT_ID=your-merchant-profile-id
CYBERSOURCE_URL=https://apitest.cybersource.com
VISA_DIRECT_URL=https://sandbox.api.visa.com/visadirect
FRONTEND_URL=http://localhost:3000

# Install dependencies
pip install cybersource-rest-client-python python-jose requests

# Start server
python api.py
```

### Step 3: Verify Setup (2 min)
```bash
# Check health
curl http://localhost:5001/api/visa/health

# Should return:
# {"visa_configured": true, ...}
```

### Step 4: Test Payment (5 min)
```bash
# Create payment session
curl -X POST http://localhost:5001/api/visa/create-payment \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "token_package": "pro"}'

# Use test card: 4111111111111111
# CVV: 123, Expiry: any future date
```

### Step 5: Add Frontend (5 min)
```tsx
// app/payment/page.tsx
import VisaPayment from '@/components/VisaPayment'

export default function PaymentPage() {
  return <VisaPayment userId="user123" />
}
```

**Done! 🎉** Your Visa integration is live.

---

## 🧪 Test with These Cards

| Card Number | Type | Result |
|-------------|------|--------|
| `4111111111111111` | Visa | ✅ Success |
| `4000000000000002` | Visa | ❌ Decline |
| `5555555555554444` | Mastercard | ✅ Success |

---

## 📊 Architecture

```
User → VisaPayment.tsx → /api/visa/create-payment
  → CyberSource checkout → Payment callback
  → Tokens credited → User can buy workflows
  → Workflow sold → Visa Direct payout to creator ⚡
```

---

## 🔍 Troubleshooting

**"visa_configured: false"**
- Check `.env` has all VISA_* variables
- Restart backend: `python api.py`

**Payment form doesn't submit**
- Check FRONTEND_URL is correct
- Verify CyberSource credentials
- Use test environment URL

**Creator payout fails**
- Use test card: `4111111111111111`
- Check you're using sandbox URL
- Verify VISA_DIRECT_URL is correct

---

## 📚 Next Steps

1. ✅ Read [VISA_INTEGRATION.md](./VISA_INTEGRATION.md) for full details
2. ✅ Check [PAYMENT_COMPARISON.md](./PAYMENT_COMPARISON.md) for alternatives
3. ✅ Test creator payouts: `/api/visa/payout-creator`
4. ✅ Add success/cancel pages
5. ✅ Deploy to production (update to prod URLs)

---

## 🏆 Demo for Visa Prize

**30-second pitch:**
> "We've integrated Visa's payment infrastructure to create an AI workflow marketplace. Users buy tokens via CyberSource, purchase workflows, and creators get paid INSTANTLY via Visa Direct. Unlike traditional marketplaces that take days for payouts, we push funds to creators' cards in seconds."

**Show:**
1. Buy tokens with Visa card → 5 seconds
2. Purchase workflow → 2 seconds
3. Creator receives payout → Instant ⚡

---

**Need help?** Check the full guide: [VISA_INTEGRATION.md](./VISA_INTEGRATION.md)
