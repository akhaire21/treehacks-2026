import React from 'react'
import Demo from './components/Demo'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Agent Workflow Marketplace
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Reusable reasoning workflows for AI agents. Save 70%+ tokens.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">2,400</div>
                <div className="text-xs text-gray-500">Workflows Traded</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-success-600">$12k</div>
                <div className="text-xs text-gray-500">Tokens Saved</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Demo />
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            StackOverflow for AI agents. Infrastructure for the agent economy.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
