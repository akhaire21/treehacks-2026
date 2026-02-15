'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import styles from './sdk.module.css'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

interface ToolCall {
  tool_name: string
  tool_input: Record<string, any>
  result: string
  latency_ms: number
}

interface AgentStep {
  step_number: number
  thinking: string
  tool_calls: ToolCall[]
  latency_ms: number
}

interface AgentTrace {
  agent_name: string
  task: string
  model: string
  steps: AgentStep[]
  final_response: string
  total_input_tokens: number
  total_output_tokens: number
  total_latency_ms: number
  tools_called: Record<string, number>
  success: boolean
}

interface Scenario {
  id: string
  title: string
  description: string
  icon: string
  prize: string
  task: string
}

// Hardcoded scenarios as fallback (works without backend)
const FALLBACK_SCENARIOS: Scenario[] = [
  {
    id: 'tax_filing',
    title: 'Ohio Tax Filing',
    description: 'Agent autonomously finds and purchases a tax workflow, then presents a step-by-step filing plan.',
    icon: '📋',
    prize: 'Anthropic — Human Flourishing',
    task: 'Help me file my Ohio 2024 taxes. I have a W2 and want to use itemized deductions. Income around $85,000.',
  },
  {
    id: 'shopping',
    title: 'Smart Product Comparison',
    description: 'Agent finds a product comparison workflow, purchases it, and delivers structured recommendations.',
    icon: '🛒',
    prize: 'Visa — Future of Commerce',
    task: 'I need to buy a laptop for software development, budget $1500-2000. Need 32GB RAM and a good screen.',
  },
  {
    id: 'orchestrator',
    title: 'Multi-Task Orchestration',
    description: 'Agent decomposes a complex relocation task into subtasks and chains marketplace workflows together.',
    icon: '🔗',
    prize: 'Greylock — Best Multi-Turn Agent',
    task: "I'm relocating from California to Ohio. Help with: 1) CA partial-year taxes, 2) Ohio tax setup, 3) Finding neighborhoods in Columbus.",
  },
]

export default function SDKPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>(FALLBACK_SCENARIOS)
  const [selectedScenario, setSelectedScenario] = useState<string>('tax_filing')
  const [trace, setTrace] = useState<AgentTrace | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [visibleSteps, setVisibleSteps] = useState(0)
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set())
  const traceRef = useRef<HTMLDivElement>(null)
  const playTimerRef = useRef<NodeJS.Timeout | null>(null)

  // Load scenarios from API
  useEffect(() => {
    fetch(`${API}/api/sdk/scenarios`)
      .then(r => r.json())
      .then(data => {
        if (data.scenarios?.length > 0) {
          setScenarios(data.scenarios)
        }
      })
      .catch(() => {}) // use fallback
  }, [])

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (playTimerRef.current) clearTimeout(playTimerRef.current)
    }
  }, [])

  const runSimulation = useCallback(async (scenarioId: string) => {
    setSelectedScenario(scenarioId)
    setTrace(null)
    setVisibleSteps(0)
    setExpandedTools(new Set())
    setIsPlaying(true)

    try {
      const res = await fetch(`${API}/api/sdk/simulate/${scenarioId}`)
      const data: AgentTrace = await res.json()
      setTrace(data)

      // Animate steps appearing one by one
      for (let i = 0; i < data.steps.length; i++) {
        await new Promise<void>(resolve => {
          playTimerRef.current = setTimeout(() => {
            setVisibleSteps(i + 1)
            resolve()
          }, 800 + i * 600)
        })
      }

      setIsPlaying(false)
    } catch {
      setIsPlaying(false)
    }
  }, [])

  const toggleTool = (key: string) => {
    setExpandedTools(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  const scrollToTrace = () => {
    traceRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const formatJson = (str: string) => {
    try {
      return JSON.stringify(JSON.parse(str), null, 2)
    } catch {
      return str
    }
  }

  return (
    <>
      <Nav />
      <main className={styles.main}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.prizeBadges}>
            <span className={styles.prizeBadge}>🏆 Anthropic — Human Flourishing</span>
            <span className={styles.prizeBadge}>🏆 Best Use of Claude Agent SDK</span>
          </div>
          <h1>
            Agent SDK
            <span className={styles.headerAccent}> Simulations</span>
          </h1>
          <p className={styles.subtitle}>
            Watch Claude agents autonomously search, buy, and use marketplace workflows
            using <code>pip install marktools</code>. Every tool call is real.
          </p>
        </div>

        {/* Architecture Diagram */}
        <div className={styles.archSection}>
          <div className={styles.archDiagram}>
            <div className={styles.archNode}>
              <div className={styles.archIcon}>🧠</div>
              <div className={styles.archLabel}>Claude</div>
              <div className={styles.archSub}>claude-sonnet-4-20250514</div>
            </div>
            <div className={styles.archArrow}>
              <span>tool_use</span>
              <div className={styles.arrowLine} />
            </div>
            <div className={styles.archNode}>
              <div className={styles.archIcon}>📦</div>
              <div className={styles.archLabel}>marktools</div>
              <div className={styles.archSub}>pip install marktools</div>
            </div>
            <div className={styles.archArrow}>
              <span>HTTP</span>
              <div className={styles.arrowLine} />
            </div>
            <div className={styles.archNode}>
              <div className={styles.archIcon}>🔍</div>
              <div className={styles.archLabel}>Mark API</div>
              <div className={styles.archSub}>Elasticsearch + JINA</div>
            </div>
          </div>
        </div>

        {/* Scenario Cards */}
        <div className={styles.scenarioSection}>
          <h2>Choose a Simulation</h2>
          <div className={styles.scenarioGrid}>
            {scenarios.map((s) => (
              <button
                key={s.id}
                className={`${styles.scenarioCard} ${selectedScenario === s.id ? styles.scenarioActive : ''}`}
                onClick={() => {
                  runSimulation(s.id)
                  setTimeout(scrollToTrace, 300)
                }}
                disabled={isPlaying}
              >
                <div className={styles.scenarioIcon}>{s.icon}</div>
                <div className={styles.scenarioContent}>
                  <h3>{s.title}</h3>
                  <p>{s.description}</p>
                  <span className={styles.scenarioPrize}>{s.prize}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Trace Replay */}
        <div ref={traceRef} className={styles.traceSection}>
          {trace && (
            <>
              <div className={styles.traceHeader}>
                <div className={styles.traceTitle}>
                  <div className={`${styles.statusDot} ${trace.success ? styles.dotGreen : styles.dotRed}`} />
                  <span>Agent Trace</span>
                </div>
                <div className={styles.traceMeta}>
                  <span>🧠 {trace.model}</span>
                  <span>⏱ {(trace.total_latency_ms / 1000).toFixed(1)}s</span>
                  <span>📥 {trace.total_input_tokens.toLocaleString()} in</span>
                  <span>📤 {trace.total_output_tokens.toLocaleString()} out</span>
                </div>
              </div>

              {/* Task */}
              <div className={styles.taskBox}>
                <div className={styles.taskLabel}>User Task</div>
                <p>{trace.task}</p>
              </div>

              {/* Steps */}
              <div className={styles.stepsContainer}>
                {trace.steps.slice(0, visibleSteps).map((step, idx) => (
                  <div
                    key={idx}
                    className={`${styles.step} ${styles.stepVisible}`}
                  >
                    <div className={styles.stepHeader}>
                      <span className={styles.stepNum}>Step {step.step_number}</span>
                      <span className={styles.stepLatency}>{step.latency_ms}ms</span>
                    </div>

                    {/* Thinking */}
                    <div className={styles.thinking}>
                      <div className={styles.thinkingLabel}>💭 Claude&apos;s Reasoning</div>
                      <p>{step.thinking}</p>
                    </div>

                    {/* Tool Calls */}
                    {step.tool_calls.map((tc, tcIdx) => {
                      const key = `${idx}-${tcIdx}`
                      const isExpanded = expandedTools.has(key)
                      return (
                        <div key={tcIdx} className={styles.toolCall}>
                          <button
                            className={styles.toolCallHeader}
                            onClick={() => toggleTool(key)}
                          >
                            <div className={styles.toolCallLeft}>
                              <span className={styles.toolIcon}>⚡</span>
                              <span className={styles.toolName}>{tc.tool_name}</span>
                              <span className={styles.toolLatency}>{tc.latency_ms}ms</span>
                            </div>
                            <span className={styles.expandIcon}>
                              {isExpanded ? '▾' : '▸'}
                            </span>
                          </button>
                          {isExpanded && (
                            <div className={styles.toolCallBody}>
                              <div className={styles.toolSection}>
                                <div className={styles.toolSectionLabel}>Input</div>
                                <pre>{JSON.stringify(tc.tool_input, null, 2)}</pre>
                              </div>
                              <div className={styles.toolSection}>
                                <div className={styles.toolSectionLabel}>Result</div>
                                <pre>{formatJson(tc.result)}</pre>
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                ))}

                {/* Loading indicator */}
                {isPlaying && visibleSteps < (trace?.steps.length ?? 0) && (
                  <div className={styles.stepLoading}>
                    <div className={styles.loadingDots}>
                      <span /><span /><span />
                    </div>
                    <span>Agent is thinking...</span>
                  </div>
                )}
              </div>

              {/* Final Response */}
              {!isPlaying && trace.final_response && (
                <div className={styles.finalResponse}>
                  <div className={styles.finalLabel}>✅ Agent Response</div>
                  <div className={styles.finalContent}>
                    {trace.final_response.split('\n').map((line, i) => (
                      <p key={i}>{line || '\u00A0'}</p>
                    ))}
                  </div>
                </div>
              )}

              {/* Stats Summary */}
              {!isPlaying && (
                <div className={styles.statsGrid}>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>{trace.steps.length}</div>
                    <div className={styles.statLabel}>Agent Steps</div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>
                      {Object.values(trace.tools_called).reduce((a, b) => a + b, 0)}
                    </div>
                    <div className={styles.statLabel}>Tool Calls</div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>
                      {((trace.total_input_tokens + trace.total_output_tokens) / 1000).toFixed(1)}k
                    </div>
                    <div className={styles.statLabel}>Total Tokens</div>
                  </div>
                  <div className={styles.statCard}>
                    <div className={styles.statValue}>
                      {(trace.total_latency_ms / 1000).toFixed(1)}s
                    </div>
                    <div className={styles.statLabel}>Total Latency</div>
                  </div>
                </div>
              )}
            </>
          )}

          {!trace && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>🤖</div>
              <p>Select a simulation above to watch an agent work.</p>
            </div>
          )}
        </div>

        {/* Code Section */}
        <div className={styles.codeSection}>
          <h2>Build Your Own Agent</h2>
          <p className={styles.codeSub}>
            Everything above runs on <code>marktools</code>. Here&apos;s how to build your own autonomous agent:
          </p>
          <pre className={styles.codeBlock}>
{`from marktools import MarkTools
from anthropic import Anthropic

# Initialize
mark = MarkTools(api_key="mk_...")
client = Anthropic()
messages = [{"role": "user", "content": "Help me file my Ohio taxes"}]

# Autonomous agent loop
while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=mark.to_anthropic(),   # ← marktools provides the tools
        messages=messages,
    )

    if response.stop_reason != "tool_use":
        print(response.content[0].text)
        break

    # Execute tool calls via marktools
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = mark.execute(block.name, block.input)  # ← marktools handles execution
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})`}
          </pre>
        </div>
      </main>
      <Footer />
    </>
  )
}
