import React from 'react'
import { motion } from 'framer-motion'
import { Sparkles, TrendingDown, Zap, Users, ArrowRight, Play } from 'lucide-react'

const Hero = ({ onGetStarted, onViewDemo }) => {
  const stats = [
    { label: 'Workflows Traded', value: '2,400+', icon: Sparkles },
    { label: 'Token Savings', value: '$12k+', icon: TrendingDown },
    { label: 'Avg. Savings', value: '70%', icon: Zap },
    { label: 'Active Users', value: '500+', icon: Users },
  ]

  return (
    <div className="relative overflow-hidden py-20 lg:py-32">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-300/30 rounded-full blur-3xl animate-float" />
        <div className="absolute top-60 -left-40 w-96 h-96 bg-purple-300/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute -bottom-40 right-20 w-80 h-80 bg-success-300/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full border border-primary-200 shadow-lg mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary-500" />
            <span className="text-sm font-semibold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
              StackOverflow for AI Agents
            </span>
          </motion.div>

          {/* Main heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 mb-6 leading-tight"
          >
            Save{' '}
            <span className="bg-gradient-to-r from-primary-600 via-purple-600 to-primary-600 bg-clip-text text-transparent animate-gradient">
              70% Tokens
            </span>
            {' '}with<br />
            Proven Workflows
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed"
          >
            Reusable reasoning workflows for AI agents. Stop reinventing the wheel.
            <br className="hidden md:block" />
            <span className="text-primary-600 font-semibold">Buy proven solutions. Save time. Save tokens.</span>
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <button
              onClick={onGetStarted}
              className="group relative px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-bold rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200 overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
              <div className="absolute inset-0 bg-gradient-shine bg-[length:200%_100%] animate-shimmer" />
            </button>

            <button
              onClick={onViewDemo}
              className="group px-8 py-4 bg-white/80 backdrop-blur-sm text-gray-900 font-bold rounded-2xl shadow-lg hover:shadow-xl border border-gray-200/50 transform hover:scale-105 transition-all duration-200"
            >
              <span className="flex items-center gap-2">
                <Play className="w-5 h-5 group-hover:scale-110 transition-transform" />
                Watch Demo
              </span>
            </button>
          </motion.div>

          {/* Stats grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                className="group relative bg-white/80 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                {/* Glow effect on hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-purple-500/0 to-primary-500/0 group-hover:from-primary-500/10 group-hover:via-purple-500/10 group-hover:to-primary-500/10 rounded-2xl transition-all duration-300" />

                <div className="relative">
                  <div className="flex justify-center mb-3">
                    <div className="p-3 bg-gradient-to-br from-primary-100 to-purple-100 rounded-xl group-hover:scale-110 transition-transform duration-300">
                      <stat.icon className="w-6 h-6 text-primary-600" />
                    </div>
                  </div>
                  <div className="text-3xl font-black text-gray-900 mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-600 font-medium">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Social proof */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.9 }}
            className="mt-12 flex items-center justify-center gap-2 text-sm text-gray-500"
          >
            <div className="flex -space-x-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-purple-400 border-2 border-white" />
              ))}
            </div>
            <span className="ml-2">Trusted by <strong className="text-gray-700">500+</strong> AI developers</span>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Hero
