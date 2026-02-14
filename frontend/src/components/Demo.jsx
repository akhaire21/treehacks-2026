import React, { useState } from 'react'
import { Search, Loader2, CheckCircle, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react'
import WorkflowCard from './WorkflowCard'
import TokenComparison from './TokenComparison'

const DEMO_SCENARIOS = [
  {
    id: 'ohio_taxes',
    label: 'Ohio Tax Filing (W2, Itemized, Married)',
    query: {
      task_type: 'tax_filing',
      state: 'ohio',
      year: 2024,
      income_bracket: '80k-100k',
      deduction_type: 'itemized',
      filing_status: 'married_jointly'
    }
  },
  {
    id: 'tokyo_trip',
    label: 'Tokyo Family Trip (5 days, kids 3-8)',
    query: {
      task_type: 'travel_planning',
      location: 'tokyo_japan',
      duration_days: 5,
      travelers: 'family_with_kids',
      accessibility: 'stroller_required'
    }
  },
  {
    id: 'stripe_invoice',
    label: 'Parse Stripe Invoice (Multi-Currency)',
    query: {
      task_type: 'data_parsing',
      platform: 'stripe',
      requirements: 'multi_currency'
    }
  }
]

const Demo = () => {
  const [step, setStep] = useState('select') // select, searching, results, purchasing, executing, comparison, rating
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [workflows, setWorkflows] = useState([])
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [progress, setProgress] = useState(0)

  // Simulate searching workflows
  const searchWorkflows = async (scenario) => {
    setSelectedScenario(scenario)
    setStep('searching')
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 10
      })
    }, 300)

    // Simulate API call
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario.query)
      })
      const data = await response.json()

      setTimeout(() => {
        clearInterval(interval)
        setWorkflows(data.results || [])
        setStep('results')
      }, 3000)
    } catch (error) {
      console.error('Search failed:', error)
      // Fallback to mock data
      setTimeout(() => {
        clearInterval(interval)
        setWorkflows(getMockWorkflows(scenario.id))
        setStep('results')
      }, 3000)
    }
  }

  // Purchase workflow
  const purchaseWorkflow = async (workflow) => {
    setSelectedWorkflow(workflow)
    setStep('purchasing')
    setProgress(0)

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 20
      })
    }, 200)

    // Simulate purchase
    setTimeout(() => {
      clearInterval(interval)
      setStep('executing')
      executeWorkflow()
    }, 1500)
  }

  // Execute workflow
  const executeWorkflow = () => {
    setProgress(0)

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 5
      })
    }, 200)

    setTimeout(() => {
      clearInterval(interval)
      setStep('comparison')
    }, 4000)
  }

  // Rate workflow
  const rateWorkflow = async (vote) => {
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.workflow_id,
          vote: vote
        })
      })
    } catch (error) {
      console.error('Rating failed:', error)
    }

    setStep('rating')
    setTimeout(() => {
      // Reset for another demo
      setTimeout(() => {
        setStep('select')
        setSelectedScenario(null)
        setWorkflows([])
        setSelectedWorkflow(null)
      }, 2000)
    }, 1500)
  }

  // Reset demo
  const resetDemo = () => {
    setStep('select')
    setSelectedScenario(null)
    setWorkflows([])
    setSelectedWorkflow(null)
    setProgress(0)
  }

  return (
    <div className="space-y-8">
      {/* Step: Select scenario */}
      {step === 'select' && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Choose a Demo Scenario</h2>
          <p className="text-gray-600 mb-6">
            See how the marketplace finds and executes pre-solved reasoning workflows
          </p>

          <div className="grid md:grid-cols-3 gap-4">
            {DEMO_SCENARIOS.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => searchWorkflows(scenario)}
                className="p-6 bg-white rounded-lg border-2 border-gray-200 hover:border-primary-500 hover:shadow-lg transition-all text-left"
              >
                <div className="flex items-start justify-between mb-2">
                  <Sparkles className="w-6 h-6 text-primary-500" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{scenario.label}</h3>
                <p className="text-sm text-gray-600">Click to search marketplace</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step: Searching */}
      {step === 'searching' && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Searching Marketplace...</h3>
            <p className="text-gray-600 mb-4">Finding workflows matching your requirements</p>

            {/* Progress bar */}
            <div className="max-w-md mx-auto">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">{progress}% complete</p>
            </div>

            {/* What's happening */}
            <div className="mt-6 text-left max-w-md mx-auto bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-700 font-medium mb-2">What's happening:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Vector similarity search across 2,400+ workflows</li>
                <li>• Hard filter: {selectedScenario?.query.task_type}, {selectedScenario?.query.state || selectedScenario?.query.location}</li>
                <li>• Ranking by embedding match score</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Step: Results */}
      {step === 'results' && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Found {workflows.length} Matching Workflows</h2>
              <p className="text-gray-600">Select a workflow to purchase and execute</p>
            </div>
            <button
              onClick={resetDemo}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Start Over
            </button>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workflows.map((workflow) => (
              <WorkflowCard
                key={workflow.workflow_id}
                workflow={workflow}
                onSelect={purchaseWorkflow}
                isSelected={false}
              />
            ))}
          </div>

          {/* Comparison preview */}
          {workflows.length > 0 && (
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>Without marketplace:</strong> Agent would spend 3,000-4,000 tokens planning this task from scratch (~8-12 seconds).
                <br />
                <strong>With marketplace:</strong> Purchase workflow (200 tokens) + execute (800 tokens) = 1,000 total tokens (~3 seconds).
                <br />
                <strong>Savings: 70%+ fewer tokens</strong>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Step: Purchasing */}
      {step === 'purchasing' && selectedWorkflow && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-success-500 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Purchasing Workflow...</h3>
            <p className="text-gray-600 mb-4">{selectedWorkflow.title}</p>

            <div className="max-w-md mx-auto">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-success-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">Downloading workflow template...</p>
            </div>
          </div>
        </div>
      )}

      {/* Step: Executing */}
      {step === 'executing' && selectedWorkflow && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Executing with Workflow...</h3>
            <p className="text-gray-600 mb-4">Running {selectedWorkflow.steps?.length || 10} steps locally</p>

            <div className="max-w-md mx-auto">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">Step {Math.floor(progress / 10)} of {selectedWorkflow.steps?.length || 10}</p>
            </div>

            {/* Executing steps */}
            <div className="mt-6 text-left max-w-md mx-auto bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-700 font-medium mb-2">Executing steps:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                {selectedWorkflow.steps?.slice(0, 3).map((step, i) => (
                  <li key={i}>• {step.thought}</li>
                )) || [
                  <li key="1">• Validating inputs and requirements</li>,
                  <li key="2">• Applying domain-specific rules</li>,
                  <li key="3">• Executing workflow logic</li>
                ]}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Step: Comparison */}
      {step === 'comparison' && selectedWorkflow && (
        <div>
          <div className="mb-6">
            <div className="flex items-center space-x-2 text-success-600 mb-2">
              <CheckCircle className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Execution Complete!</h2>
            </div>
            <p className="text-gray-600">Here's how using the marketplace saved tokens:</p>
          </div>

          <TokenComparison
            fromScratch={selectedWorkflow.token_comparison?.from_scratch || 3200}
            withWorkflow={selectedWorkflow.token_cost + (selectedWorkflow.execution_tokens || 800)}
            workflowCost={selectedWorkflow.token_cost}
          />

          {/* Rate workflow */}
          <div className="mt-8 bg-white rounded-lg shadow-lg border border-gray-200 p-6 text-center">
            <h3 className="text-lg font-bold text-gray-900 mb-2">How was this workflow?</h3>
            <p className="text-gray-600 mb-4">Your feedback helps improve marketplace quality</p>

            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={() => rateWorkflow('up')}
                className="flex items-center space-x-2 px-6 py-3 bg-success-500 hover:bg-success-600 text-white rounded-lg transition-colors"
              >
                <ThumbsUp className="w-5 h-5" />
                <span>Helpful</span>
              </button>
              <button
                onClick={() => rateWorkflow('down')}
                className="flex items-center space-x-2 px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                <ThumbsDown className="w-5 h-5" />
                <span>Not Helpful</span>
              </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={resetDemo}
              className="px-6 py-2 text-primary-600 hover:text-primary-700 font-medium"
            >
              Try Another Scenario →
            </button>
          </div>
        </div>
      )}

      {/* Step: Rating submitted */}
      {step === 'rating' && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8 text-center">
          <CheckCircle className="w-16 h-16 text-success-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Thank you!</h3>
          <p className="text-gray-600">Your feedback has been recorded.</p>
          <p className="text-sm text-gray-500 mt-4">Returning to start...</p>
        </div>
      )}
    </div>
  )
}

// Mock workflow data for demo
const getMockWorkflows = (scenarioId) => {
  const mockData = {
    ohio_taxes: [
      {
        workflow_id: 'ohio_w2_itemized_2024',
        title: 'Ohio 2024 IT-1040 (W2, Itemized, Married)',
        description: 'Complete Ohio state income tax filing for W2 employees with itemized deductions filing married jointly.',
        token_cost: 200,
        execution_tokens: 800,
        rating: 4.8,
        usage_count: 47,
        tags: ['tax', 'ohio', 'w2', 'itemized', 'married'],
        match_percentage: 95,
        token_comparison: {
          from_scratch: 3200,
          with_workflow: 1000,
          savings_percent: 69
        },
        steps: [
          { thought: 'Ohio requires local tax jurisdiction code - agents often miss this' },
          { thought: 'Calculate Ohio AGI - differs from federal' },
          { thought: 'Apply Ohio-specific deductions' }
        ]
      }
    ],
    tokyo_trip: [
      {
        workflow_id: 'tokyo_family_trip_5day',
        title: 'Tokyo 5-Day Family Trip (Kids 3-8, Stroller Accessible)',
        description: 'Complete Tokyo itinerary for families with young children requiring stroller accessibility.',
        token_cost: 220,
        execution_tokens: 900,
        rating: 4.7,
        usage_count: 34,
        tags: ['travel', 'tokyo', 'family', 'kids', 'stroller'],
        match_percentage: 92,
        token_comparison: {
          from_scratch: 4200,
          with_workflow: 1120,
          savings_percent: 73
        },
        steps: [
          { thought: 'Tokyo metro stroller accessibility varies by station' },
          { thought: 'Plan around nap times and kid-friendly restaurants' },
          { thought: 'Include backup activities for rainy days' }
        ]
      }
    ],
    stripe_invoice: [
      {
        workflow_id: 'stripe_invoice_parser_multicurrency',
        title: 'Stripe Invoice Parser (Multi-Currency, Line Items)',
        description: 'Parse Stripe invoices extracting customer details, line items, currency conversion, taxes, and payment status.',
        token_cost: 150,
        execution_tokens: 600,
        rating: 4.9,
        usage_count: 156,
        tags: ['stripe', 'invoice', 'parsing', 'finance'],
        match_percentage: 98,
        token_comparison: {
          from_scratch: 2200,
          with_workflow: 750,
          savings_percent: 66
        },
        steps: [
          { thought: 'Extract invoice metadata and customer details' },
          { thought: 'Parse line items with subscription vs one-time categorization' },
          { thought: 'Handle currency conversion if needed' }
        ]
      }
    ]
  }

  return mockData[scenarioId] || []
}

export default Demo
