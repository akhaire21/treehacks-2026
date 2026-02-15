'use client'

import { useState } from 'react'

export default function TestVisaPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Test payment creation
  const testPayment = async (packageType: string) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:5001/api/visa/create-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'test_user_' + Date.now(),
          token_package: packageType,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setResult(data)

        // Auto-submit to CyberSource for testing
        const form = document.createElement('form')
        form.method = 'POST'
        form.action = data.payment_url

        Object.entries(data.form_data).forEach(([key, value]) => {
          const input = document.createElement('input')
          input.type = 'hidden'
          input.name = key
          input.value = value as string
          form.appendChild(input)
        })

        document.body.appendChild(form)
        form.submit()
      } else {
        setError('Payment creation failed: ' + JSON.stringify(data))
      }
    } catch (err) {
      setError('Error: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  // Test payout
  const testPayout = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:5001/api/visa/payout-creator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          creator_id: 'test_creator_123',
          card_number: '4111111111111111',
          amount_tokens: 1700,
          workflow_id: 'test_workflow',
        }),
      })

      const data = await response.json()
      setResult(data)

      if (!data.success) {
        setError('Payout failed: ' + JSON.stringify(data))
      }
    } catch (err) {
      setError('Error: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  // Check Visa health
  const checkHealth = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:5001/api/visa/health')
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Error: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">🧪 Visa Payment Testing</h1>
        <p className="text-gray-600 mb-8">
          Test Visa CyberSource payments and Visa Direct payouts
        </p>

        {/* Health Check */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">1. Check Visa Integration Status</h2>
          <button
            onClick={checkHealth}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            Check Health
          </button>
        </div>

        {/* Payment Testing */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">2. Test Token Purchase (CyberSource)</h2>
          <p className="text-sm text-gray-600 mb-4">
            Click to create payment and redirect to CyberSource test page.
            <br />
            <strong>Test Card:</strong> 4111111111111111 | CVV: 123 | Expiry: 12/2025
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => testPayment('starter')}
              disabled={loading}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
              Starter ($10)
            </button>
            <button
              onClick={() => testPayment('pro')}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              Pro ($45)
            </button>
            <button
              onClick={() => testPayment('enterprise')}
              disabled={loading}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
            >
              Enterprise ($120)
            </button>
          </div>
        </div>

        {/* Payout Testing */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">3. Test Creator Payout (Visa Direct)</h2>
          <p className="text-sm text-gray-600 mb-4">
            Test instant payout to creator's card (1700 tokens = $17)
          </p>
          <button
            onClick={testPayout}
            disabled={loading}
            className="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 disabled:bg-gray-400"
          >
            Test Payout ($17)
          </button>
        </div>

        {/* Results Display */}
        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">⏳ Loading...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="font-bold text-red-800 mb-2">❌ Error</h3>
            <pre className="text-sm text-red-700 whitespace-pre-wrap">{error}</pre>
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h3 className="font-bold text-green-800 mb-2">✅ Result</h3>
            <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}

        {/* Test Cards Reference */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h3 className="font-bold mb-3">📝 Test Cards for CyberSource</h3>
          <div className="text-sm space-y-2">
            <div className="flex justify-between">
              <span className="font-mono">4111111111111111</span>
              <span className="text-green-600">✅ Success</span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono">4000000000000002</span>
              <span className="text-red-600">❌ Decline</span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono">5555555555554444</span>
              <span className="text-green-600">✅ Mastercard</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-300">
            <p className="text-xs text-gray-600">
              <strong>CVV:</strong> 123 | <strong>Expiry:</strong> 12/2025 | <strong>ZIP:</strong> 94105
            </p>
          </div>
        </div>

        {/* Documentation Link */}
        <div className="mt-6 text-center">
          <a
            href="/VISA_TESTING_GUIDE.md"
            className="text-blue-600 hover:underline"
            target="_blank"
          >
            📚 View Full Testing Guide
          </a>
        </div>
      </div>
    </div>
  )
}
