import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Filter, X, TrendingUp, Star, DollarSign } from 'lucide-react'
import WorkflowCard from './WorkflowCard'

const Browse = ({ onSelectWorkflow }) => {
  const [workflows, setWorkflows] = useState([])
  const [filteredWorkflows, setFilteredWorkflows] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState('popular') // popular, rating, tokens
  const [loading, setLoading] = useState(true)

  const categories = [
    { id: 'all', label: 'All Workflows', count: 0 },
    { id: 'tax_filing', label: 'Tax Filing', count: 0 },
    { id: 'travel_planning', label: 'Travel Planning', count: 0 },
    { id: 'data_parsing', label: 'Data Parsing', count: 0 },
    { id: 'real_estate', label: 'Real Estate', count: 0 },
    { id: 'outreach', label: 'Outreach', count: 0 },
  ]

  // Fetch workflows
  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/workflows')
      const data = await response.json()
      setWorkflows(data.workflows || [])
      setFilteredWorkflows(data.workflows || [])
    } catch (error) {
      console.error('Failed to fetch workflows:', error)
      // Fallback to mock data if API fails
      setWorkflows([])
      setFilteredWorkflows([])
    } finally {
      setLoading(false)
    }
  }

  // Filter and sort workflows
  useEffect(() => {
    let filtered = [...workflows]

    // Apply category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(w => w.task_type === selectedCategory)
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(w =>
        w.title.toLowerCase().includes(query) ||
        w.description.toLowerCase().includes(query) ||
        w.tags?.some(tag => tag.toLowerCase().includes(query))
      )
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return (b.usage_count || 0) - (a.usage_count || 0)
        case 'rating':
          return (b.rating || 0) - (a.rating || 0)
        case 'tokens':
          return (a.token_cost || 0) - (b.token_cost || 0)
        default:
          return 0
      }
    })

    setFilteredWorkflows(filtered)
  }, [workflows, selectedCategory, searchQuery, sortBy])

  // Get category counts
  const getCategoryCount = (categoryId) => {
    if (categoryId === 'all') return workflows.length
    return workflows.filter(w => w.task_type === categoryId).length
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 text-center"
        >
          <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
            Browse <span className="gradient-text">Workflows</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover proven reasoning workflows from the community
          </p>
        </motion.div>

        {/* Search and filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card-glass mb-8 space-y-6"
        >
          {/* Search bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search workflows, tags, or descriptions..."
              className="w-full pl-12 pr-12 py-4 bg-white/50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            )}
          </div>

          {/* Category filters */}
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-xl font-medium transition-all ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg'
                    : 'bg-white/50 text-gray-700 hover:bg-white hover:shadow-md'
                }`}
              >
                {category.label}
                <span className="ml-2 opacity-75">({getCategoryCount(category.id)})</span>
              </button>
            ))}
          </div>

          {/* Sort options */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Filter className="w-4 h-4" />
              <span className="font-medium">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 bg-white/50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="popular">Most Popular</option>
                <option value="rating">Highest Rated</option>
                <option value="tokens">Lowest Token Cost</option>
              </select>
            </div>

            <div className="text-sm text-gray-600">
              <strong>{filteredWorkflows.length}</strong> workflow{filteredWorkflows.length !== 1 ? 's' : ''} found
            </div>
          </div>
        </motion.div>

        {/* Loading state */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            ))}
          </div>
        )}

        {/* Workflows grid */}
        {!loading && filteredWorkflows.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <AnimatePresence mode="popLayout">
              {filteredWorkflows.map((workflow, index) => (
                <motion.div
                  key={workflow.workflow_id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05, duration: 0.3 }}
                >
                  <WorkflowCard
                    workflow={workflow}
                    onSelect={() => onSelectWorkflow(workflow)}
                    isSelected={false}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Empty state */}
        {!loading && filteredWorkflows.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No workflows found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your search or filters</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
              }}
              className="btn-ghost"
            >
              Clear Filters
            </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Browse
