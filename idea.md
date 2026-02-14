# Agent Workflow Marketplace - Hackathon Build

## Core Idea
StackOverflow for AI agents. Reusable reasoning workflows for specific tasks that save 70%+ tokens by letting agents buy pre-solved reasoning patterns instead of re-planning every time.

## The Problem
- Agents waste 10-25% tokens on planning (decomposing tasks, deciding tool calls, handling errors)
- Same specific tasks get re-solved repeatedly (e.g., "file Ohio taxes", "parse Stripe invoice")
- Too specific to train separate models, but common enough to be valuable

## The Solution
Marketplace where agents buy/sell domain-specific reasoning workflows:
- User's agent queries marketplace: "File Ohio 2024 taxes, W2, itemized deductions"
- Finds workflow: ohio_taxes_w2_itemized (47 uses, 4.8★, 200 tokens)
- Purchases workflow, executes locally with private data
- Saves ~12,000 tokens vs solving from scratch

## Key Insight: SPECIFICITY
Workflows are NOT generic patterns. They're hyper-specific:
- ❌ "Tax filing workflow" (too vague)
- ✅ "Ohio 2024 IT-1040, W2 income, itemized deductions, married filing jointly"

500K people file Ohio taxes annually → narrow + large audience = valuable

## Architecture

### Option B: Marketplace as API/Tool (Build This)
```
User's Agent → Marketplace API → Returns workflow → Agent executes locally
```

**Core API:**
- `POST /api/search` - Find matching workflows (vector similarity + hard filters)
- `POST /api/purchase` - Buy workflow, returns execution template
- `POST /api/feedback` - Rate workflow (upvote/downvote)

**Demo Wrapper (for pitch):**
- Pretty UI that calls the API internally
- Shows token savings side-by-side
- Workflow marketplace cards (like Airbnb listings)

### Privacy-First Design
**Two-layer architecture:**

**Layer 1 - Public (sent to marketplace):**
```json
{
  "task_type": "tax_filing",
  "state": "ohio",
  "year": 2024,
  "income_bracket": "80k-100k",  // Bucketed, not exact
  "deduction_type": "itemized"
}
```

**Layer 2 - Private (stays local):**
```json
{
  "name": "John Smith",
  "ssn": "123-45-6789",
  "exact_income": 87432.18,
  // ... never sent to marketplace
}
```

Workflows are TEMPLATES with placeholders. Agent fills in private data locally.

## What a Workflow Is

**JSON structure capturing:**
1. Decision tree (what to ask)
2. Tool sequence (what to call, in order)
3. Validation rules (what to check)
4. Edge cases (what could go wrong)
5. Domain knowledge (Ohio has NO SALT cap, needs local tax code, etc.)

**Example snippet:**
```json
{
  "workflow_id": "ohio_w2_itemized_2024",
  "steps": [
    {
      "step": 1,
      "thought": "Ohio requires local tax jurisdiction - agents often miss this",
      "action": "web_search",
      "query": "Ohio local tax jurisdiction for {user_city}",
      "extract": "jurisdiction_code"
    },
    {
      "step": 2,
      "action": "calculate",
      "formula": "ohio_agi = federal_agi - state_pension",
      "ohio_specific": "NO $10k SALT cap (differs from federal)"
    }
  ],
  "validations": [...],
  "edge_cases": [...]
}
```

## Hackathon Scope (30 hours, 4 people)

### Team Split
- **Person 1:** Frontend (React UI, token visualization, workflow cards)
- **Person 2:** Backend API (Flask/FastAPI, search/purchase/rate endpoints)
- **Person 3:** Content (write 8-10 hyper-specific workflows as JSON)
- **Person 4:** Integration/pitch (wire together, slides, demo rehearsal)

### Tech Stack
- Frontend: React + Tailwind (deploy to Vercel)
- Backend: Flask/FastAPI (deploy to Railway/Render)
- Database: JSON file with mock workflows (no real DB needed)
- Embeddings: `sentence-transformers` (all-MiniLM-L6-v2)
- NO real LLM calls (mock everything, use pre-generated outputs)

### Workflow Matching
```python
from sentence_transformers import SentenceTransformer

# 1. Hard filter (exact match required)
candidates = [wf for wf in workflows 
              if wf["state"] == query["state"] 
              and wf["task_type"] == query["task_type"]]

# 2. Rank by embedding similarity
model = SentenceTransformer('all-MiniLM-L6-v2')
query_text = "Task: tax_filing | State: ohio | Income: 80-100k"
query_emb = model.encode(query_text)

for wf in candidates:
    similarity = cosine_similarity(query_emb, wf_embedding)
    # Sort by similarity, return top 10
```

### 8-10 Example Workflows (Hyper-Specific)
1. Ohio 2024 IT-1040, W2, itemized, married filing jointly
2. California 2024 Form 540, W2, standard deduction
3. Tokyo 5-day family trip (kids 3-8, stroller needed)
4. Stripe invoice parser (multi-currency, line items)
5. Zillow Columbus OH homes (3bed+, <$400k, school rating >7)
6. LinkedIn cold outreach B2B SaaS (polite, relationship-preserving)
7. Nebraska 2024 tax filing, self-employed, quarterly estimates
8. PDF medical records parser (extract vitals, medications)

Each workflow: 100-300 lines JSON with steps, validations, edge cases, domain knowledge.

### Demo Flow
1. User uploads invoice.pdf
2. Show two paths:
   - **From scratch:** 3,500 tokens, 12 sec (simulated)
   - **Use marketplace:** 200 token purchase + 800 execution = 1,000 total
3. Click "Use Market" → shows 3 matching workflows
4. Purchase one → execution animation
5. Side-by-side token comparison (visual bar chart)
6. "Rate workflow" → thumbs up/down
7. Show rating updated: 4.8 → 4.9

### Key Files to Build

**Backend:**
- `workflows.json` - Mock DB with 10 workflows
- `api.py` - Search/purchase/rate endpoints
- `matcher.py` - Embedding-based search logic
- `sanitizer.py` - Privacy filter (remove PII from queries)

**Frontend:**
- `WorkflowCard.jsx` - Display workflow (price, rating, description)
- `TokenComparison.jsx` - Side-by-side bar chart
- `Demo.jsx` - Main demo flow

**Content:**
- 8-10 workflow JSON files with full reasoning traces

### Pitch Deck (10 slides)
1. Problem: Agents waste tokens re-solving specific tasks
2. Solution: Marketplace for reasoning workflows
3. Demo: Live token savings
4. Specificity: Why "Ohio taxes" not "tax filing"
5. Privacy: Two-layer architecture
6. Network effects: Quality workflows dominate
7. Business model: Transaction fees (20%)
8. Market size: Millions of specific tasks × token savings
9. Traction: Mock metrics (2,400 workflows traded, $12k saved)
10. Vision: Infrastructure for agent economy

### Timeline (30 hours)
- **Hours 0-2:** Team alignment, tech setup, define API contract
- **Hours 2-12:** Parallel build (frontend/backend/content/integration)
- **Hours 12-14:** Integration checkpoint, debug together
- **Hours 14-20:** Polish features, add animations, finish workflows
- **Hours 20-24:** Rehearse pitch 5x, record backup video
- **Hours 24-28:** Final polish, deploy, test on different devices
- **Hours 28-30:** Sleep 1 hour, final prep

## Competitive Moats
1. Network effects (more usage → better workflows → more users)
2. Domain-specific knowledge base (can't be replicated by training)
3. Quality curation (tiered validation system)
4. Privacy-first architecture (workflows are templates, not data)

## Success Metrics for Demo
- Show 70%+ token savings on 3+ different tasks
- Workflows have realistic ratings/usage stats
- Privacy sanitization visible (show before/after query)
- Demo runs smoothly in <3 min pitch

## One-Liner
"StackOverflow for AI agents. Reuse proven reasoning workflows for specific tasks. Save 70% tokens. Privacy-preserving. Infrastructure for the agent economy."

## Critical: DON'T Build
- ❌ Real LLM integration (too slow, mock it)
- ❌ User authentication (guest mode only)
- ❌ Payment processing (show token counts)
- ❌ Complex DAG execution engine
- ❌ Custom embedding models (use sentence-transformers)

## DO Build
- ✅ Beautiful token comparison visualization
- ✅ 8-10 detailed, realistic workflow JSONs
- ✅ Privacy sanitizer that shows before/after
- ✅ Working search/purchase/rate flow
- ✅ Rehearsed 3-min pitch with backup video