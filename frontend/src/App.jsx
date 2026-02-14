import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Layers, PlayCircle, Menu, X as XIcon, Sun, Moon } from 'lucide-react'
import Hero from './components/Hero'
import Browse from './components/Browse'
import Demo from './components/Demo'
import WorkflowDetails from './components/WorkflowDetails'

function App() {
  const [currentView, setCurrentView] = useState('home') // home, browse, demo
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

  const navigation = [
    { id: 'home', label: 'Home', icon: Sparkles },
    { id: 'browse', label: 'Browse', icon: Layers },
    { id: 'demo', label: 'Demo', icon: PlayCircle },
  ]

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleNavigate = (viewId) => {
    setCurrentView(viewId)
    setMobileMenuOpen(false)
    scrollToTop()
  }

  const handleWorkflowSelect = (workflow) => {
    setSelectedWorkflow(workflow)
  }

  const handlePurchaseWorkflow = (workflow) => {
    console.log('Purchasing workflow:', workflow)
    // This would integrate with the Demo component flow
    setCurrentView('demo')
    scrollToTop()
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      {/* Navigation Header */}
      <header className="sticky top-0 z-30 glass border-b border-white/20 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => handleNavigate('home')}
            >
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-black text-gray-900">
                  Agent <span className="gradient-text">Marketplace</span>
                </h1>
                <p className="text-xs text-gray-600 font-medium">Save 70%+ tokens</p>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              {navigation.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all ${
                    currentView === item.id
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-white/80 hover:shadow-md'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Stats and Actions */}
            <div className="flex items-center gap-4">
              {/* Stats - Hidden on mobile */}
              <div className="hidden lg:flex items-center gap-6">
                <div className="text-right">
                  <div className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                    2.4k
                  </div>
                  <div className="text-xs text-gray-600 font-medium">Workflows</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold bg-gradient-to-r from-success-600 to-success-700 bg-clip-text text-transparent">
                    $12k
                  </div>
                  <div className="text-xs text-gray-600 font-medium">Saved</div>
                </div>
              </div>

              {/* Dark mode toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-xl hover:bg-white/50 transition-colors"
              >
                {darkMode ? (
                  <Sun className="w-5 h-5 text-gray-700" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-700" />
                )}
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-xl hover:bg-white/50 transition-colors"
              >
                {mobileMenuOpen ? (
                  <XIcon className="w-6 h-6 text-gray-700" />
                ) : (
                  <Menu className="w-6 h-6 text-gray-700" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="md:hidden border-t border-white/20 py-4 space-y-2"
              >
                {navigation.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleNavigate(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold transition-all ${
                      currentView === item.id
                        ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-white/80'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    {item.label}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative">
        <AnimatePresence mode="wait">
          {currentView === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Hero
                onGetStarted={() => handleNavigate('browse')}
                onViewDemo={() => handleNavigate('demo')}
              />

              {/* Features Section */}
              <section className="py-20 bg-white/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                  <div className="text-center mb-16">
                    <h2 className="text-4xl font-black text-gray-900 mb-4">
                      Why Use the <span className="gradient-text">Marketplace</span>?
                    </h2>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                      Stop wasting tokens on planning. Buy proven workflows.
                    </p>
                  </div>

                  <div className="grid md:grid-cols-3 gap-8">
                    {[
                      {
                        title: 'Save 70% Tokens',
                        description: 'Pre-built reasoning workflows eliminate 10-25% token waste on planning and tool selection.',
                        icon: '💎',
                        gradient: 'from-primary-400 to-primary-600'
                      },
                      {
                        title: 'Domain Expertise',
                        description: 'Workflows capture nuanced domain knowledge that agents often miss when starting from scratch.',
                        icon: '🧠',
                        gradient: 'from-purple-400 to-purple-600'
                      },
                      {
                        title: 'Privacy First',
                        description: 'Only send sanitized queries to marketplace. Your sensitive data never leaves your system.',
                        icon: '🔒',
                        gradient: 'from-success-400 to-success-600'
                      }
                    ].map((feature, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * i }}
                        className="card-glass text-center group hover:scale-105"
                      >
                        <div className={`text-6xl mb-4 transform group-hover:scale-110 transition-transform`}>
                          {feature.icon}
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                        <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </section>
            </motion.div>
          )}

          {currentView === 'browse' && (
            <motion.div
              key="browse"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Browse onSelectWorkflow={handleWorkflowSelect} />
            </motion.div>
          )}

          {currentView === 'demo' && (
            <motion.div
              key="demo"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="py-12"
            >
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                  <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
                    Interactive <span className="gradient-text">Demo</span>
                  </h1>
                  <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                    See how the marketplace finds and executes workflows in real-time
                  </p>
                </div>
                <Demo />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-br from-gray-900 to-gray-800 text-white py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-2xl font-black">Agent Marketplace</h3>
            </div>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              StackOverflow for AI agents. Reuse proven reasoning workflows for specific tasks.
              Save 70% tokens. Privacy-preserving. Infrastructure for the agent economy.
            </p>
            <div className="flex items-center justify-center gap-6 text-sm text-gray-400">
              <span>Built for TreeHacks 2026 🌲</span>
              <span>•</span>
              <span>Made with ❤️ by the team</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Workflow Details Modal */}
      <WorkflowDetails
        workflow={selectedWorkflow}
        onClose={() => setSelectedWorkflow(null)}
        onPurchase={handlePurchaseWorkflow}
      />
    </div>
  )
}

export default App
