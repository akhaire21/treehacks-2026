'use client'

import { useState } from 'react'

interface TokenPackage {
  id: string
  name: string
  tokens: string
  price: string
  priceValue: number
  discount?: string
  popular?: boolean
}

export default function VisaPayment({ userId }: { userId: string }) {
  const [loading, setLoading] = useState(false)
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)

  const packages: TokenPackage[] = [
    {
      id: 'starter',
      name: 'Starter',
      tokens: '1,000',
      price: '$10',
      priceValue: 10,
    },
    {
      id: 'pro',
      name: 'Professional',
      tokens: '5,000',
      price: '$45',
      priceValue: 45,
      discount: 'Save 10%',
      popular: true,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      tokens: '15,000',
      price: '$120',
      priceValue: 120,
      discount: 'Save 20%',
    },
  ]

  const handlePurchase = async (packageId: string) => {
    setLoading(true)
    setSelectedPackage(packageId)

    try {
      // Step 1: Create Visa payment session
      const response = await fetch('http://localhost:5001/api/visa/create-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          token_package: packageId,
        }),
      })

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || 'Failed to create payment session')
      }

      // Step 2: Create a form and submit to CyberSource
      const form = document.createElement('form')
      form.method = 'POST'
      form.action = result.payment_url

      // Add all form fields from response
      Object.entries(result.form_data).forEach(([key, value]) => {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = key
        input.value = value as string
        form.appendChild(input)
      })

      document.body.appendChild(form)
      form.submit()

    } catch (error) {
      console.error('Payment error:', error)
      alert(`Payment failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setLoading(false)
      setSelectedPackage(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Purchase Tokens</h2>
        <p className="text-gray-600">
          Buy tokens to purchase AI workflow templates. Secure payment powered by{' '}
          <span className="font-semibold text-blue-600">Visa</span>
        </p>
      </div>

      {/* Visa Badge */}
      <div className="flex justify-center mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-6 py-3 flex items-center gap-3">
          <svg className="w-6 h-6 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 4h16v16H4z" opacity="0.3"/>
            <path d="M21.5 8.5h-3L17 13l-1.5-4.5h-3L14 13l-1.5-4.5h-3L11 13 9.5 8.5h-3L8 13l-1.5-4.5h-3L5 13H2v2h4l1.5-4.5L9 15h2l1.5-4.5L14 15h2l1.5-4.5L19 15h4v-2h-3l1.5-4.5z"/>
          </svg>
          <span className="text-sm font-medium text-gray-700">
            Secured by Visa Developer Platform
          </span>
        </div>
      </div>

      {/* Package Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <div
            key={pkg.id}
            className={`relative border-2 rounded-xl p-6 transition-all ${
              pkg.popular
                ? 'border-blue-500 shadow-lg scale-105'
                : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
            }`}
          >
            {/* Popular Badge */}
            {pkg.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                  MOST POPULAR
                </span>
              </div>
            )}

            {/* Package Name */}
            <h3 className="text-xl font-bold text-center mb-2">{pkg.name}</h3>

            {/* Tokens */}
            <div className="text-center mb-4">
              <div className="text-4xl font-bold text-gray-900">{pkg.tokens}</div>
              <div className="text-sm text-gray-500">tokens</div>
            </div>

            {/* Price */}
            <div className="text-center mb-4">
              <div className="text-3xl font-bold text-blue-600">{pkg.price}</div>
              {pkg.discount && (
                <div className="text-sm text-green-600 font-semibold mt-1">
                  {pkg.discount}
                </div>
              )}
            </div>

            {/* Value Proposition */}
            <div className="text-center text-sm text-gray-600 mb-6">
              {pkg.id === 'starter' && '2-3 workflow purchases'}
              {pkg.id === 'pro' && '10-12 workflow purchases'}
              {pkg.id === 'enterprise' && '30+ workflow purchases'}
            </div>

            {/* Purchase Button */}
            <button
              onClick={() => handlePurchase(pkg.id)}
              disabled={loading}
              className={`w-full py-3 rounded-lg font-semibold transition-all ${
                loading && selectedPackage === pkg.id
                  ? 'bg-gray-400 cursor-not-allowed'
                  : pkg.popular
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
              }`}
            >
              {loading && selectedPackage === pkg.id ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Processing...
                </span>
              ) : (
                `Purchase ${pkg.name}`
              )}
            </button>

            {/* Features */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Instant activation
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  No expiration
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Secure payment via Visa
                </li>
              </ul>
            </div>
          </div>
        ))}
      </div>

      {/* Security Notice */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-gray-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
          <div className="text-sm text-gray-600">
            <strong className="font-semibold">Secure Payment Processing:</strong> All payments
            are processed securely through Visa CyberSource. We never store your full card
            details. Transactions are encrypted and PCI-DSS compliant.
          </div>
        </div>
      </div>
    </div>
  )
}
