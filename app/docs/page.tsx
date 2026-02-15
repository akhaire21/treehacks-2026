'use client'

import { useEffect, useState } from 'react'
import styles from './page.module.css'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

export default function DocsPage() {
  const [activeTab, setActiveTab] = useState('quickstart')
  const [sdkInfo, setSdkInfo] = useState<any>(null)
  const [tools, setTools] = useState<any[]>([])
  const [examples, setExamples] = useState<any>(null)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/sdk/info`).then(r => r.json()).catch(() => null),
      fetch(`${API}/api/sdk/tools`).then(r => r.json()).catch(() => ({ tools: [] })),
      fetch(`${API}/api/sdk/examples`).then(r => r.json()).catch(() => null),
    ]).then(([info, toolsData, examplesData]) => {
      setSdkInfo(info)
      setTools(toolsData.tools || [])
      setExamples(examplesData)
    })
  }, [])

  return (
    <>
      <Nav />
      <main className={styles.main}>
        <div className={styles.header}>
          <span className={styles.badge}>SDK Documentation</span>
          <h1>marktools</h1>
          <p className={styles.subtitle}>
            The Python SDK that lets AI agents buy pre-solved reasoning workflows.
          </p>
          <div className={styles.installBox}>
            <code>pip install marktools</code>
          </div>
        </div>

        <div className={styles.tabs}>
          {['quickstart', 'anthropic', 'openai', 'client', 'tools', 'models'].map((tab) => (
            <button
              key={tab}
              className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'quickstart' ? 'Quick Start' :
               tab === 'anthropic' ? 'Anthropic' :
               tab === 'openai' ? 'OpenAI' :
               tab === 'client' ? 'Client' :
               tab === 'tools' ? 'Tools' :
               'Models'}
            </button>
          ))}
        </div>

        <div className={styles.content}>
          {activeTab === 'quickstart' && (
            <div className={styles.section}>
              <h2>Quick Start</h2>
              <p>Get started with marktools in 3 lines of code.</p>

              <h3>Installation</h3>
              <pre className={styles.codeBlock}>
{`pip install marktools

# With framework extras
pip install marktools[anthropic]   # Anthropic Claude support
pip install marktools[openai]      # OpenAI GPT support
pip install marktools[all]         # All frameworks`}
              </pre>

              <h3>Basic Usage</h3>
              <pre className={styles.codeBlock}>
{`from marktools import MarkClient

mark = MarkClient(api_key="mk_...")  # or set MARK_API_KEY env var

# 1. Estimate — is the marketplace worth it? (free, no credits)
estimate = mark.estimate("File Ohio 2024 taxes with W2 and itemized deductions")

# 2. Buy — purchase the best solution
receipt = mark.buy(estimate.session_id, estimate.best_solution.solution_id)

# 3. Use — step-by-step instructions, edge cases, domain knowledge
for wf in receipt.execution_plan.workflows:
    print(f"📋 {wf.workflow_title}")
    for step in wf.workflow.steps:
        print(f"  Step {step['step']}: {step['thought']}")`}
              </pre>

              <h3>One-Shot Solve</h3>
              <pre className={styles.codeBlock}>
{`# Auto-estimate + auto-buy the best solution in one call
receipt = mark.solve("File Ohio 2024 taxes with W2 and itemized deductions")
print(f"Tokens charged: {receipt.tokens_charged}")`}
              </pre>

              <h3>Environment Variables</h3>
              <table className={styles.table}>
                <thead>
                  <tr><th>Variable</th><th>Description</th><th>Default</th></tr>
                </thead>
                <tbody>
                  <tr><td><code>MARK_API_KEY</code></td><td>Your API key</td><td>—</td></tr>
                  <tr><td><code>MARK_API_URL</code></td><td>API base URL</td><td><code>https://api.mark.ai</code></td></tr>
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'anthropic' && (
            <div className={styles.section}>
              <h2>Use with Anthropic Claude</h2>
              <p>
                marktools provides native Anthropic tool_use format. Claude can autonomously
                search, buy, and rate marketplace workflows.
              </p>
              <pre className={styles.codeBlock}>
{`from marktools import MarkTools
from anthropic import Anthropic

mark = MarkTools(api_key="mk_...")
client = Anthropic()

# Pass Mark tools alongside your own tools
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=mark.to_anthropic(),
    messages=[{"role": "user", "content": "Help me file my Ohio taxes for 2024"}],
)

# Handle tool calls in your agent loop
for block in response.content:
    if block.type == "tool_use":
        result = mark.execute(block.name, block.input)
        # Return result to Claude as tool_result`}
              </pre>

              <h3>Full Agent Loop Example</h3>
              <pre className={styles.codeBlock}>
{`from marktools import MarkTools
from anthropic import Anthropic

mark = MarkTools(api_key="mk_...")
client = Anthropic()
messages = [{"role": "user", "content": "Help me file my Ohio taxes"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=mark.to_anthropic(),
        messages=messages,
    )

    if response.stop_reason == "tool_use":
        # Claude wants to use a Mark tool
        assistant_content = []
        tool_results = []

        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use", "id": block.id,
                    "name": block.name, "input": block.input
                })
                result = mark.execute(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})
    else:
        # Final response
        print(response.content[0].text)
        break`}
              </pre>
            </div>
          )}

          {activeTab === 'openai' && (
            <div className={styles.section}>
              <h2>Use with OpenAI GPT-4</h2>
              <p>
                marktools generates OpenAI-compatible function calling definitions.
                Works with GPT-4o, GPT-4, and any model that supports function calling.
              </p>
              <pre className={styles.codeBlock}>
{`from marktools import MarkTools
from openai import OpenAI
import json

mark = MarkTools(api_key="mk_...")
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    tools=mark.to_openai(),
    messages=[{"role": "user", "content": "Help me file my Ohio taxes"}],
)

# Execute tool calls
for call in response.choices[0].message.tool_calls or []:
    result = mark.execute(
        call.function.name,
        json.loads(call.function.arguments)
    )
    print(f"Tool: {call.function.name}")
    print(f"Result: {result[:200]}")`}
              </pre>
            </div>
          )}

          {activeTab === 'client' && (
            <div className={styles.section}>
              <h2>MarkClient Reference</h2>
              <p>The core HTTP client for direct API access.</p>

              <h3>Initialization</h3>
              <pre className={styles.codeBlock}>
{`from marktools import MarkClient

# API key from parameter
mark = MarkClient(api_key="mk_...")

# API key from environment
# export MARK_API_KEY=mk_...
mark = MarkClient()

# Custom server (self-hosted)
mark = MarkClient(base_url="http://localhost:5001")`}
              </pre>

              <h3>Methods</h3>
              <table className={styles.table}>
                <thead>
                  <tr><th>Method</th><th>Cost</th><th>Description</th></tr>
                </thead>
                <tbody>
                  <tr><td><code>estimate(query)</code></td><td>Free</td><td>Search & get ranked solutions with pricing</td></tr>
                  <tr><td><code>buy(session_id, solution_id)</code></td><td>Credits</td><td>Purchase solution, get full execution plan</td></tr>
                  <tr><td><code>rate(workflow_id, rating)</code></td><td>Free</td><td>Rate a workflow after use</td></tr>
                  <tr><td><code>search(**filters)</code></td><td>Free</td><td>Search marketplace with filters</td></tr>
                  <tr><td><code>solve(query)</code></td><td>Credits</td><td>One-shot: estimate + buy best solution</td></tr>
                  <tr><td><code>balance()</code></td><td>Free</td><td>Check credit balance</td></tr>
                  <tr><td><code>sanitize(data)</code></td><td>Free</td><td>Preview PII sanitization</td></tr>
                  <tr><td><code>health()</code></td><td>Free</td><td>API health check</td></tr>
                  <tr><td><code>chat(message)</code></td><td>Free</td><td>Talk to the Claude agent</td></tr>
                  <tr><td><code>list_workflows()</code></td><td>Free</td><td>List all available workflows</td></tr>
                </tbody>
              </table>

              <h3>Privacy Sanitization</h3>
              <pre className={styles.codeBlock}>
{`result = mark.sanitize({
    "name": "John Smith",         # ← removed
    "ssn": "123-45-6789",         # ← removed
    "exact_income": 87432.18,     # ← bucketed to "80k-100k"
    "state": "ohio",              # ← kept
    "year": 2024,                 # ← kept
})
# public_query: {"state": "ohio", "year": 2024, "exact_income": "80k-100k"}
# private_data: {"name": "John Smith", "ssn": "123-45-6789"}`}
              </pre>
            </div>
          )}

          {activeTab === 'tools' && (
            <div className={styles.section}>
              <h2>Tool Definitions</h2>
              <p>marktools exposes 4 tools that AI agents can call:</p>

              {tools.length > 0 ? (
                tools.map((tool: any, i: number) => (
                  <div key={i} className={styles.toolDef}>
                    <h3>{tool.name}</h3>
                    <p>{tool.description}</p>
                    <pre className={styles.codeBlock}>
                      {JSON.stringify(tool.input_schema, null, 2)}
                    </pre>
                  </div>
                ))
              ) : (
                <div className={styles.toolDef}>
                  <h3>mark_estimate</h3>
                  <p>Search the marketplace and get pricing. Free, no credits spent.</p>
                  <pre className={styles.codeBlock}>
{`{
  "query": "string (required) — task description",
  "context": "object (optional) — metadata, PII auto-sanitized"
}`}
                  </pre>

                  <h3>mark_buy</h3>
                  <p>Purchase a solution. Returns full execution plan.</p>
                  <pre className={styles.codeBlock}>
{`{
  "session_id": "string (required) — from mark_estimate",
  "solution_id": "string (required) — e.g. 'sol_1'"
}`}
                  </pre>

                  <h3>mark_rate</h3>
                  <p>Rate a workflow after use.</p>
                  <pre className={styles.codeBlock}>
{`{
  "workflow_id": "string (required)",
  "rating": "integer (1-5)",
  "vote": "'up' | 'down'"
}`}
                  </pre>

                  <h3>mark_search</h3>
                  <p>Browse marketplace with filters.</p>
                  <pre className={styles.codeBlock}>
{`{
  "query": "string — search text",
  "task_type": "string — category filter",
  "state": "string — US state",
  "year": "integer"
}`}
                  </pre>
                </div>
              )}

              <h3>Format Conversion</h3>
              <pre className={styles.codeBlock}>
{`from marktools import MarkTools

tools = MarkTools(api_key="mk_...")

# Anthropic Claude format
tools.to_anthropic()

# OpenAI function calling format
tools.to_openai()

# LangChain format
tools.to_langchain()

# Raw JSON schema
tools.to_json_schema()`}
              </pre>
            </div>
          )}

          {activeTab === 'models' && (
            <div className={styles.section}>
              <h2>Response Models</h2>
              <p>All API responses are typed Pydantic models with full IDE autocomplete.</p>

              <pre className={styles.codeBlock}>
{`from marktools import (
    Workflow,           # Marketplace workflow template
    Solution,           # Ranked solution candidate
    EstimateResult,     # Response from estimate()
    PurchaseReceipt,    # Response from buy()
    RateResult,         # Response from rate()
    SearchResult,       # Search result with score
    Subtask,            # Decomposed subtask
)`}
              </pre>

              <h3>Workflow</h3>
              <pre className={styles.codeBlock}>
{`workflow.workflow_id     # "ohio_w2_itemized_2024"
workflow.title           # "Ohio 2024 IT-1040 (W2, Itemized)"
workflow.total_cost      # 1000 (download_cost + execution_cost)
workflow.rating          # 4.8
workflow.num_steps       # 10
workflow.steps           # [{"step": 1, "thought": "...", "action": "..."}]
workflow.edge_cases      # ["If city has multiple jurisdictions..."]
workflow.domain_knowledge  # ["Ohio does NOT have $10k SALT cap..."]`}
              </pre>

              <h3>EstimateResult</h3>
              <pre className={styles.codeBlock}>
{`estimate.session_id          # "sess_abc123" — use in buy()
estimate.num_solutions       # 3
estimate.best_solution       # Solution with rank=1
estimate.cheapest_solution   # Solution with lowest cost
estimate.solutions[0].pricing.total_cost_tokens    # 500
estimate.solutions[0].pricing.savings_percentage   # 70`}
              </pre>

              <h3>PurchaseReceipt</h3>
              <pre className={styles.codeBlock}>
{`receipt.purchase_id          # "purchase_abc123"
receipt.tokens_charged       # 500
receipt.execution_plan.workflows[0].workflow_title  # "Ohio Tax Filing"
receipt.execution_plan.workflows[0].workflow.steps  # [...]
receipt.execution_plan.execution_order              # ["subtask_0", ...]`}
              </pre>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  )
}
