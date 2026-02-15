'use client'

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import styles from './AgentChat.module.css'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

interface Message {
  role: 'user' | 'agent' | 'system'
  content: string
  toolCalls?: string[]
  timestamp?: string
}

const SUGGESTED_PROMPTS = [
  { label: 'Search for tax filing workflows', icon: '🔍', tool: 'mark_estimate' },
  { label: 'Find shopping comparison tools', icon: '🔍', tool: 'mark_estimate' },
  { label: 'Buy the best tax workflow for Ohio', icon: '💳', tool: 'mark_buy' },
  { label: 'Purchase a product comparison workflow', icon: '💳', tool: 'mark_buy' },
]

const MARK_TOOLS = [
  {
    name: 'mark_estimate',
    label: 'Search',
    icon: '🔍',
    description: 'Search the marketplace for pre-solved workflows. Free — no credits spent.',
    endpoint: 'POST /api/estimate',
    color: '#00bfae',
  },
  {
    name: 'mark_buy',
    label: 'Buy',
    icon: '💳',
    description: 'Purchase a solution and receive the full execution plan. Deducts credits.',
    endpoint: 'POST /api/buy',
    color: '#ffd700',
  },
]

export default function AgentChat() {
  const sectionRef = useRef<HTMLElement>(null)
  const messagesRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: 'Agent session started — Claude is ready. Ask me anything about the marketplace.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [tokenBalance, setTokenBalance] = useState<number | null>(null)
  const [sessionStats, setSessionStats] = useState({ searches: 0, purchases: 0, ratings: 0 })
  const [connected, setConnected] = useState(false)

  // Check backend health on mount
  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => r.json())
      .then((d) => {
        setConnected(d.agent_enabled === true)
        if (!d.agent_enabled) {
          setMessages((prev) => [
            ...prev,
            { role: 'system', content: '⚠ Agent is offline — backend not connected' },
          ])
        }
      })
      .catch(() => setConnected(false))

    // Reset agent session for clean demo
    fetch(`${API}/api/agent/reset`, { method: 'POST' }).catch(() => {})
  }, [])

  // Intersection observer for fade-in
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.1 }
    )
    if (sectionRef.current) observer.observe(sectionRef.current)
    return () => {
      if (sectionRef.current) observer.unobserve(sectionRef.current)
    }
  }, [])

  // Auto-scroll messages
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = async (text?: string) => {
    const msg = text || input.trim()
    if (!msg || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: msg, timestamp: new Date().toLocaleTimeString() }])
    setLoading(true)

    try {
      const res = await fetch(`${API}/api/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      })

      const data = await res.json()

      if (data.error) {
        setMessages((prev) => [
          ...prev,
          { role: 'system', content: `Error: ${data.error}` },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'agent',
            content: data.response,
            toolCalls: data.tool_calls?.map((tc: { tool: string }) => tc.tool) || [],
            timestamp: new Date().toLocaleTimeString(),
          },
        ])

        if (data.token_balance !== undefined) setTokenBalance(data.token_balance)
        if (data.session_stats) setSessionStats(data.session_stats)
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: 'Network error — is the backend running on port 5001?' },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const resetSession = async () => {
    try {
      await fetch(`${API}/api/agent/reset`, { method: 'POST' })
      setMessages([{ role: 'system', content: 'Session reset — fresh conversation started.' }])
      setTokenBalance(null)
      setSessionStats({ searches: 0, purchases: 0, ratings: 0 })
    } catch {
      // ignore
    }
  }

  return (
    <section ref={sectionRef} className={`${styles.section} fade-in`} id="agent">
      <div className={styles.container}>
        <div className={styles.sectionLabel}>Live Agent Demo</div>
        <h2 className={styles.sectionTitle}>
          Talk to the agent.
          <br />
          Watch it work.
        </h2>
        <p className={styles.sectionSub}>
          This is a live Claude-powered agent with autonomous tool use. It searches the
          Elasticsearch marketplace, evaluates workflows, manages your token economy, and
          executes multi-step tasks — all in real time.
        </p>

        {/* Mark Tools Panel */}
        <div className={styles.toolsPanel}>
          <div className={styles.toolsPanelLabel}>Agent SDK Tools</div>
          <div className={styles.toolCards}>
            {MARK_TOOLS.map((tool) => (
              <div key={tool.name} className={styles.toolCard} style={{ '--tool-color': tool.color } as React.CSSProperties}>
                <div className={styles.toolCardHeader}>
                  <span className={styles.toolCardIcon}>{tool.icon}</span>
                  <span className={styles.toolCardName}>{tool.name}</span>
                  <span className={styles.toolCardEndpoint}>{tool.endpoint}</span>
                </div>
                <div className={styles.toolCardDesc}>{tool.description}</div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.chatWrapper}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatHeaderLeft}>
              <div className={`${styles.statusDot} ${connected ? '' : styles.statusDotOff}`} />
              <div>
                <div className={styles.chatHeaderTitle}>mark-agent</div>
                <div className={styles.chatHeaderSub}>
                  Claude claude-sonnet-4-20250514 · {connected ? 'connected' : 'offline'}
                </div>
              </div>
            </div>
            <div className={styles.chatHeaderRight}>
              <button className={styles.sessionBtn} onClick={resetSession}>
                Reset
              </button>
              {tokenBalance !== null && (
                <span className={styles.tokenBadge}>◈ {tokenBalance.toLocaleString()}</span>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className={styles.messages} ref={messagesRef}>
            {messages.map((msg, i) => (
              <div key={i} className={`${styles.message} ${styles[`message${msg.role.charAt(0).toUpperCase() + msg.role.slice(1)}`]}`}>
                {msg.role !== 'system' && (
                  <div className={styles.messageMeta}>
                    <span className={styles.messageLabel}>
                      {msg.role === 'user' ? 'You' : 'Agent'}
                    </span>
                    {msg.timestamp && <span>{msg.timestamp}</span>}
                  </div>
                )}
                <div className={`${styles.messageBubble} ${msg.role === 'agent' ? styles.markdown : ''}`}>
                  {msg.role === 'agent' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.toolCalls && msg.toolCalls.length > 0 && (
                  <div className={styles.toolCalls}>
                    {msg.toolCalls.map((tool, j) => {
                      const isSearch = tool.includes('search') || tool.includes('estimate') || tool.includes('evaluate') || tool.includes('sanitize') || tool.includes('complexity')
                      const isBuy = tool.includes('purchase') || tool.includes('buy') || tool.includes('execute') || tool.includes('compare')
                      return (
                        <span
                          key={j}
                          className={`${styles.toolBadge} ${isSearch ? styles.toolBadgeSearch : ''} ${isBuy ? styles.toolBadgeBuy : ''}`}
                        >
                          {isSearch ? '🔍' : isBuy ? '💳' : '⚡'} {tool}
                        </span>
                      )
                    })}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.messageAgent}`}>
                <div className={styles.messageMeta}>
                  <span className={styles.messageLabel}>Agent</span>
                </div>
                <div className={`${styles.messageBubble} ${styles.typing}`}>
                  <div className={styles.typingDot} />
                  <div className={styles.typingDot} />
                  <div className={styles.typingDot} />
                </div>
              </div>
            )}
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && (
            <div className={styles.suggestions}>
              {SUGGESTED_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  className={`${styles.suggestion} ${prompt.tool === 'mark_buy' ? styles.suggestionBuy : styles.suggestionSearch}`}
                  onClick={() => sendMessage(prompt.label)}
                >
                  <span className={styles.suggestionIcon}>{prompt.icon}</span>
                  {prompt.label}
                </button>
              ))}
            </div>
          )}

          {/* Stats bar */}
          <div className={styles.statsBar}>
            <span className={styles.stat}>
              searches <span className={styles.statVal}>{sessionStats.searches}</span>
            </span>
            <span className={styles.stat}>
              purchases <span className={styles.statVal}>{sessionStats.purchases}</span>
            </span>
            <span className={styles.stat}>
              ratings <span className={styles.statVal}>{sessionStats.ratings}</span>
            </span>
          </div>

          {/* Input */}
          <div className={styles.inputArea}>
            <input
              ref={inputRef}
              className={styles.inputField}
              type="text"
              placeholder={loading ? 'Agent is thinking...' : 'Ask the agent anything...'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              disabled={loading}
            />
            <button
              className={styles.sendBtn}
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
