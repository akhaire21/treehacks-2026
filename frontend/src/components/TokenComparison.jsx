import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { TrendingDown, Zap, Clock } from 'lucide-react'

const TokenComparison = ({ fromScratch, withWorkflow, workflowCost }) => {
  const data = [
    {
      name: 'From Scratch',
      tokens: fromScratch,
      fill: '#ef4444', // red
      time: Math.round(fromScratch / 100) // rough estimate: 100 tokens/sec
    },
    {
      name: 'With Marketplace',
      tokens: withWorkflow,
      fill: '#22c55e', // green
      time: Math.round(withWorkflow / 100)
    }
  ]

  const savings = fromScratch - withWorkflow
  const savingsPercent = Math.round((savings / fromScratch) * 100)
  const costSavings = (savings * 0.00003).toFixed(2) // Rough: $0.03 per 1k tokens

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Token Comparison</h3>

      {/* Chart */}
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Tokens', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              formatter={(value) => value.toLocaleString() + ' tokens'}
              labelStyle={{ color: '#000' }}
            />
            <Bar dataKey="tokens" radius={[8, 8, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-4">
        {/* Token savings */}
        <div className="bg-success-50 rounded-lg p-4">
          <div className="flex items-center text-success-700 mb-1">
            <TrendingDown className="w-5 h-5 mr-2" />
            <span className="text-sm font-medium">Token Savings</span>
          </div>
          <div className="text-2xl font-bold text-success-700">
            {savingsPercent}%
          </div>
          <div className="text-xs text-success-600 mt-1">
            {savings.toLocaleString()} tokens saved
          </div>
        </div>

        {/* Cost savings */}
        <div className="bg-primary-50 rounded-lg p-4">
          <div className="flex items-center text-primary-700 mb-1">
            <Zap className="w-5 h-5 mr-2" />
            <span className="text-sm font-medium">Cost Savings</span>
          </div>
          <div className="text-2xl font-bold text-primary-700">
            ${costSavings}
          </div>
          <div className="text-xs text-primary-600 mt-1">
            per execution
          </div>
        </div>

        {/* Time savings */}
        <div className="bg-amber-50 rounded-lg p-4">
          <div className="flex items-center text-amber-700 mb-1">
            <Clock className="w-5 h-5 mr-2" />
            <span className="text-sm font-medium">Time Savings</span>
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {Math.round((data[0].time - data[1].time) / 60)} min
          </div>
          <div className="text-xs text-amber-600 mt-1">
            faster execution
          </div>
        </div>
      </div>

      {/* Breakdown */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Breakdown</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Workflow Purchase:</span>
            <span className="font-semibold text-gray-900">{workflowCost.toLocaleString()} tokens</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Execution (with template):</span>
            <span className="font-semibold text-gray-900">{(withWorkflow - workflowCost).toLocaleString()} tokens</span>
          </div>
          <div className="flex justify-between pt-2 border-t border-gray-200">
            <span className="text-gray-700 font-medium">Total:</span>
            <span className="font-bold text-gray-900">{withWorkflow.toLocaleString()} tokens</span>
          </div>
          <div className="flex justify-between text-gray-500 text-xs">
            <span>vs. planning from scratch:</span>
            <span>{fromScratch.toLocaleString()} tokens</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TokenComparison
