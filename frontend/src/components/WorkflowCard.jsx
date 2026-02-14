import React from 'react'
import { Star, TrendingUp, Coins } from 'lucide-react'

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
    <div
      onClick={() => onSelect(workflow)}
      className={`
        relative bg-white rounded-lg border-2 p-6 cursor-pointer transition-all duration-200
        hover:shadow-lg hover:-translate-y-1
        ${isSelected
          ? 'border-primary-500 shadow-lg ring-2 ring-primary-200'
          : 'border-gray-200 hover:border-primary-300'
        }
      `}
    >
      {/* Match percentage badge */}
      {match_percentage && (
        <div className="absolute top-4 right-4 bg-success-50 text-success-700 px-3 py-1 rounded-full text-sm font-semibold">
          {match_percentage}% match
        </div>
      )}

      {/* Title and description */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 line-clamp-2">{description}</p>
      </div>

      {/* Stats row */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <div className="flex items-center space-x-4">
          {/* Rating */}
          <div className="flex items-center text-amber-500">
            <Star className="w-4 h-4 fill-current mr-1" />
            <span className="font-semibold">{rating}</span>
          </div>

          {/* Usage count */}
          <div className="flex items-center text-gray-600">
            <TrendingUp className="w-4 h-4 mr-1" />
            <span>{usage_count} uses</span>
          </div>
        </div>

        {/* Token cost */}
        <div className="flex items-center text-primary-600 font-semibold">
          <Coins className="w-4 h-4 mr-1" />
          <span>{token_cost} tokens</span>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {tags.slice(0, 4).map((tag, index) => (
          <span
            key={index}
            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
          >
            {tag}
          </span>
        ))}
        {tags.length > 4 && (
          <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md">
            +{tags.length - 4} more
          </span>
        )}
      </div>

      {/* Token savings preview */}
      {token_comparison && (
        <div className="pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Estimated savings:</div>
          <div className="text-lg font-bold text-success-600">
            {token_comparison.savings_percent}% fewer tokens
          </div>
          <div className="text-xs text-gray-500">
            {token_comparison.from_scratch.toLocaleString()} → {' '}
            {(token_cost + (workflow.execution_tokens || 0)).toLocaleString()} tokens
          </div>
        </div>
      )}

      {/* Select indicator */}
      {isSelected && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-success-500 rounded-t-lg" />
      )}
    </div>
  )
}

export default WorkflowCard
