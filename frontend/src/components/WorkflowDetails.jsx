import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Star, TrendingUp, Coins, Clock, CheckCircle, AlertCircle, Download, ExternalLink } from 'lucide-react'

const WorkflowDetails = ({ workflow, onClose, onPurchase }) => {
  if (!workflow) return null

  const {
    workflow_id,
    title,
    description,
    token_cost,
    execution_tokens,
    rating,
    usage_count,
    tags,
    steps,
    requirements,
    edge_cases,
    domain_knowledge,
    estimated_time_saved,
    token_comparison
  } = workflow

  return (
    <AnimatePresence>
      {workflow && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-4 md:inset-8 lg:inset-16 bg-white rounded-3xl shadow-2xl z-50 overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6 md:p-8">
              <button
                onClick={onClose}
                className="absolute top-6 right-6 p-2 hover:bg-white/20 rounded-xl transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              <div className="max-w-4xl mx-auto">
                <h2 className="text-3xl md:text-4xl font-black mb-4">{title}</h2>
                <p className="text-lg text-white/90 mb-6">{description}</p>

                {/* Stats row */}
                <div className="flex flex-wrap gap-6">
                  <div className="flex items-center gap-2">
                    <Star className="w-5 h-5 fill-current" />
                    <span className="font-bold text-lg">{rating}</span>
                    <span className="text-white/80 text-sm">rating</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    <span className="font-bold text-lg">{usage_count}</span>
                    <span className="text-white/80 text-sm">uses</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Coins className="w-5 h-5" />
                    <span className="font-bold text-lg">{token_cost}</span>
                    <span className="text-white/80 text-sm">tokens</span>
                  </div>
                  {estimated_time_saved && (
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      <span className="text-white/80 text-sm">{estimated_time_saved}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 md:p-8">
              <div className="max-w-4xl mx-auto space-y-8">
                {/* Tags */}
                <div>
                  <div className="flex flex-wrap gap-2">
                    {tags?.map((tag, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 bg-primary-50 text-primary-700 text-sm font-medium rounded-lg"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Token savings */}
                {token_comparison && (
                  <div className="card-glass">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-success-600" />
                      Token Savings
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600 mb-1">From Scratch</div>
                        <div className="text-2xl font-bold text-danger-600">
                          {token_comparison.from_scratch?.toLocaleString()} tokens
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">With Workflow</div>
                        <div className="text-2xl font-bold text-success-600">
                          {token_comparison.with_workflow?.toLocaleString()} tokens
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="text-3xl font-black text-success-600">
                        {token_comparison.savings_percent}% savings
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Save {(token_comparison.from_scratch - token_comparison.with_workflow)?.toLocaleString()} tokens per execution
                      </div>
                    </div>
                  </div>
                )}

                {/* Requirements */}
                {requirements && requirements.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-primary-600" />
                      Requirements
                    </h3>
                    <div className="bg-gray-50 rounded-xl p-4">
                      <ul className="space-y-2">
                        {requirements.map((req, i) => (
                          <li key={i} className="flex items-start gap-2 text-gray-700">
                            <CheckCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                            <span>{req}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Steps */}
                {steps && steps.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Workflow Steps</h3>
                    <div className="space-y-3">
                      {steps.slice(0, 5).map((step, i) => (
                        <div key={i} className="flex gap-4 bg-white border border-gray-200 rounded-xl p-4">
                          <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 text-white rounded-lg flex items-center justify-center font-bold">
                            {step.step || i + 1}
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900 mb-1">{step.thought}</div>
                            {step.action && (
                              <div className="text-sm text-gray-600">Action: {step.action}</div>
                            )}
                          </div>
                        </div>
                      ))}
                      {steps.length > 5 && (
                        <div className="text-center text-gray-600 text-sm font-medium">
                          + {steps.length - 5} more steps
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Edge cases */}
                {edge_cases && edge_cases.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-warning-600" />
                      Edge Cases Handled
                    </h3>
                    <div className="space-y-3">
                      {edge_cases.slice(0, 3).map((edge, i) => (
                        <div key={i} className="bg-warning-50 border border-warning-200 rounded-xl p-4">
                          <div className="font-semibold text-warning-900 mb-1">{edge.scenario}</div>
                          <div className="text-sm text-warning-800">{edge.handling}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Domain knowledge */}
                {domain_knowledge && domain_knowledge.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Domain Knowledge</h3>
                    <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                      <ul className="space-y-2">
                        {domain_knowledge.slice(0, 4).map((knowledge, i) => (
                          <li key={i} className="flex items-start gap-2 text-purple-900 text-sm">
                            <span className="text-purple-600 font-bold flex-shrink-0">•</span>
                            <span>{knowledge}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 p-6 md:p-8 bg-gray-50">
              <div className="max-w-4xl mx-auto flex items-center justify-between gap-4 flex-wrap">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Total Cost</div>
                  <div className="text-3xl font-black text-gray-900">
                    {token_cost + (execution_tokens || 0)} tokens
                  </div>
                  <div className="text-sm text-gray-600">
                    {token_cost} purchase + {execution_tokens || 800} execution
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={onClose}
                    className="btn-ghost"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => {
                      onPurchase(workflow)
                      onClose()
                    }}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Purchase & Execute
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default WorkflowDetails
