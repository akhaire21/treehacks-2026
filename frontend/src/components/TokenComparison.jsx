import React from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { TrendingDown, Zap, Clock, DollarSign, Award } from 'lucide-react'

const TokenComparison = ({ fromScratch, withWorkflow, workflowCost }) => {
  const data = [
    {
      name: 'From Scratch',
      tokens: fromScratch,
      fill: '#ef4444', // danger red
      time: Math.round(fromScratch / 100) // rough estimate: 100 tokens/sec
    },
    {
      name: 'With Marketplace',
      tokens: withWorkflow,
      fill: '#22c55e', // success green
      time: Math.round(withWorkflow / 100)
    }
  ]

  const savings = fromScratch - withWorkflow
  const savingsPercent = Math.round((savings / fromScratch) * 100)
  const costSavings = (savings * 0.00003).toFixed(2) // Rough: $0.03 per 1k tokens
  const timeSaved = Math.round((data[0].time - data[1].time) / 60)

  const statCards = [
    {
      icon: TrendingDown,
      label: 'Token Savings',
      value: `${savingsPercent}%`,
      subtitle: `${savings.toLocaleString()} tokens saved`,
      gradient: 'from-success-500 to-success-600',
      bg: 'bg-success-50'
    },
    {
      icon: DollarSign,
      label: 'Cost Savings',
      value: `$${costSavings}`,
      subtitle: 'per execution',
      gradient: 'from-primary-500 to-primary-600',
      bg: 'bg-primary-50'
    },
    {
      icon: Clock,
      label: 'Time Savings',
      value: `${timeSaved} min`,
      subtitle: 'faster execution',
      gradient: 'from-amber-500 to-amber-600',
      bg: 'bg-amber-50'
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-glass overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-black text-gray-900 mb-1 flex items-center gap-2">
            <Award className="w-6 h-6 text-primary-600" />
            Token Comparison
          </h3>
          <p className="text-sm text-gray-600">See how much you save with the marketplace</p>
        </div>
      </div>

      {/* Chart */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-8 bg-white/50 rounded-xl p-4 border border-gray-100"
      >
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#6b7280', fontWeight: 600 }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              label={{ value: 'Tokens', angle: -90, position: 'insideLeft', fill: '#6b7280', fontWeight: 600 }}
              tick={{ fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip
              formatter={(value) => [value.toLocaleString() + ' tokens', '']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                padding: '12px',
                fontWeight: 600
              }}
              labelStyle={{ color: '#111827', fontWeight: 'bold' }}
            />
            <Bar dataKey="tokens" radius={[12, 12, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            className={`${stat.bg} rounded-xl p-5 border border-gray-100 group hover:scale-105 transition-transform duration-300`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2.5 bg-gradient-to-br ${stat.gradient} rounded-xl shadow-lg`}>
                <stat.icon className="w-5 h-5 text-white" />
              </div>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5 + index * 0.1, type: 'spring' }}
                className="text-xs font-bold text-gray-500 bg-white px-2 py-1 rounded-full"
              >
                NEW
              </motion.div>
            </div>
            <div className={`text-3xl font-black bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent mb-1`}>
              {stat.value}
            </div>
            <div className="text-sm font-medium text-gray-700 mb-1">{stat.label}</div>
            <div className="text-xs text-gray-600">{stat.subtitle}</div>
          </motion.div>
        ))}
      </div>

      {/* Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="pt-6 border-t border-gray-200 bg-gradient-to-br from-gray-50/50 to-primary-50/50 -mx-6 -mb-6 px-6 py-6 rounded-b-2xl"
      >
        <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary-600" />
          Cost Breakdown
        </h4>
        <div className="space-y-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="flex justify-between items-center p-3 bg-white rounded-xl border border-gray-200"
          >
            <span className="text-gray-700 font-medium">Workflow Purchase</span>
            <span className="font-black text-primary-600">{workflowCost.toLocaleString()} tokens</span>
          </motion.div>

          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="flex justify-between items-center p-3 bg-white rounded-xl border border-gray-200"
          >
            <span className="text-gray-700 font-medium">Execution (with template)</span>
            <span className="font-black text-primary-600">{(withWorkflow - workflowCost).toLocaleString()} tokens</span>
          </motion.div>

          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ delay: 0.9, duration: 0.5 }}
            className="flex justify-between items-center p-4 bg-gradient-to-r from-primary-500 to-purple-600 rounded-xl shadow-lg"
          >
            <span className="text-white font-bold">Total Cost</span>
            <span className="font-black text-white text-lg">{withWorkflow.toLocaleString()} tokens</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
            className="flex justify-between text-sm pt-2 border-t border-gray-200"
          >
            <span className="text-gray-600">vs. planning from scratch</span>
            <span className="text-gray-900 font-bold line-through">{fromScratch.toLocaleString()} tokens</span>
          </motion.div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default TokenComparison
