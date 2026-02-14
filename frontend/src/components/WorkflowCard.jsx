import React from 'react'
import { motion } from 'framer-motion'
import { Star, TrendingUp, Coins, Zap, ExternalLink } from 'lucide-react'

const WorkflowCard = ({ workflow, onSelect, isSelected }) => {
  const {
    workflow_id,
    title,
    description,
    token_cost,
    rating,
    usage_count,
    tags,
    match_percentage,
    token_comparison
  } = workflow

  return (
    <motion.div
      onClick={() => onSelect(workflow)}
      className={`
        relative bg-white rounded-2xl border-2 p-6 cursor-pointer transition-all duration-300
        hover:shadow-2xl hover:-translate-y-2 group overflow-hidden
        ${isSelected
          ? 'border-primary-500 shadow-2xl shadow-primary-200 ring-4 ring-primary-100'
          : 'border-gray-200 hover:border-primary-300'
        }
      `}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-500/0 via-purple-500/0 to-primary-500/0
                      group-hover:from-primary-500/5 group-hover:via-purple-500/5 group-hover:to-primary-500/5
                      transition-all duration-300 rounded-2xl pointer-events-none" />

      {/* Match percentage badge */}
      {match_percentage && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-4 right-4 z-10"
        >
          <div className="bg-gradient-to-r from-success-500 to-success-600 text-white px-3 py-1.5 rounded-full text-sm font-bold shadow-lg flex items-center gap-1">
            <Zap className="w-3 h-3" />
            {match_percentage}% match
          </div>
        </motion.div>
      )}

      {/* Content */}
      <div className="relative z-10">
        {/* Title and description */}
        <div className="mb-4 pr-16">
          <h3 className="text-xl font-black text-gray-900 mb-2 group-hover:text-primary-600 transition-colors leading-tight">
            {title}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">{description}</p>
        </div>

        {/* Stats row */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
          <div className="flex items-center gap-4">
            {/* Rating */}
            <motion.div
              className="flex items-center gap-1"
              whileHover={{ scale: 1.1 }}
            >
              <div className="p-1.5 bg-amber-50 rounded-lg">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              </div>
              <div>
                <div className="font-bold text-gray-900 text-sm">{rating}</div>
                <div className="text-xs text-gray-500">rating</div>
              </div>
            </motion.div>

            {/* Usage count */}
            <motion.div
              className="flex items-center gap-1"
              whileHover={{ scale: 1.1 }}
            >
              <div className="p-1.5 bg-primary-50 rounded-lg">
                <TrendingUp className="w-4 h-4 text-primary-600" />
              </div>
              <div>
                <div className="font-bold text-gray-900 text-sm">{usage_count}</div>
                <div className="text-xs text-gray-500">uses</div>
              </div>
            </motion.div>
          </div>

          {/* Token cost */}
          <motion.div
            className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-primary-50 to-purple-50 rounded-xl"
            whileHover={{ scale: 1.05 }}
          >
            <Coins className="w-5 h-5 text-primary-600" />
            <div>
              <div className="font-black text-primary-600 text-sm">{token_cost}</div>
              <div className="text-xs text-primary-600/70">tokens</div>
            </div>
          </motion.div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {tags?.slice(0, 4).map((tag, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="px-2.5 py-1 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-primary-50 hover:to-purple-50
                         text-gray-700 hover:text-primary-700 text-xs font-medium rounded-lg transition-all cursor-pointer border border-gray-200"
            >
              {tag}
            </motion.span>
          ))}
          {tags && tags.length > 4 && (
            <span className="px-2.5 py-1 bg-gray-50 text-gray-500 text-xs font-medium rounded-lg border border-gray-200">
              +{tags.length - 4}
            </span>
          )}
        </div>

        {/* Token savings preview */}
        {token_comparison && (
          <motion.div
            className="pt-4 border-t border-gray-200 bg-gradient-to-br from-success-50/50 to-primary-50/50 -mx-6 -mb-6 px-6 py-4 rounded-b-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium text-gray-600 mb-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-success-600" />
                  Estimated savings
                </div>
                <div className="text-2xl font-black bg-gradient-to-r from-success-600 to-success-700 bg-clip-text text-transparent">
                  {token_comparison.savings_percent}%
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500 line-through">
                  {token_comparison.from_scratch?.toLocaleString()}
                </div>
                <div className="text-sm font-bold text-success-600">
                  → {(token_cost + (workflow.execution_tokens || 0)).toLocaleString()} tokens
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Hover indicator */}
      <motion.div
        className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-primary-500 via-purple-500 to-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={{ scaleX: 0 }}
        whileHover={{ scaleX: 1 }}
      />

      {/* Click indicator icon */}
      <motion.div
        className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity"
        whileHover={{ scale: 1.2, rotate: -45 }}
      >
        <ExternalLink className="w-5 h-5 text-primary-600" />
      </motion.div>
    </motion.div>
  )
}

export default WorkflowCard
