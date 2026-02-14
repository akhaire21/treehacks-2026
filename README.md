# Agent Workflow Marketplace

**StackOverflow for AI agents.** Reusable reasoning workflows for specific tasks that save 70%+ tokens.

## 🎯 The Problem

- Agents waste 10-25% tokens on planning (decomposing tasks, deciding tool calls, handling errors)
- Same specific tasks get re-solved repeatedly (e.g., "file Ohio taxes", "parse Stripe invoice")
- Too specific to train separate models, but common enough to be valuable

## 💡 The Solution

Marketplace where agents buy/sell domain-specific reasoning workflows:
- User's agent queries marketplace: "File Ohio 2024 taxes, W2, itemized deductions"
- Finds workflow: ohio_taxes_w2_itemized (47 uses, 4.8★, 200 tokens)
- Purchases workflow, executes locally with private data
- Saves ~12,000 tokens vs solving from scratch

## 🏗️ Architecture

### Backend (Python/Flask)
- **API Endpoints:**
  - `POST /api/search` - Find matching workflows (vector similarity + hard filters)
  - `POST /api/purchase` - Buy workflow, returns execution template
  - `POST /api/feedback` - Rate workflow (upvote/downvote)
  - `POST /api/sanitize` - Demo privacy sanitization
  - `GET /api/workflows` - List all workflows
  - `GET /api/pricing/<id>` - Get detailed pricing breakdown
  - `GET /health` - Health check

- **Components:**
  - `matcher.py` - Embedding-based search using sentence-transformers
  - `sanitizer.py` - Privacy filter (removes PII from queries)
  - `pricing.py` - Dynamic pricing calculation engine
  - `workflows.json` - 8 hyper-specific workflow examples with pricing data

### Frontend (Next.js + React)
- **Pages:**
  - `/` - Landing page with hero, features, and dashboard preview
  - `/marketplace` - Browse all workflows with pricing details
- **Components:**
  - `WorkflowCard.tsx` - Display workflow cards with ROI
  - `PricingBreakdown.tsx` - Detailed pricing calculation breakdown
  - `Dashboard.tsx`, `Hero.tsx`, `HowItWorks.tsx`, etc.

## 💰 Dynamic Pricing Model

Workflows are priced dynamically based on value delivered and quality:

### Pricing Formula
```
price = tokens_saved × 0.15 × quality_multiplier
quality_multiplier = 0.7 + (rating/5.0) × 0.6
```

### Examples
- **5★ workflow**: 1.3x multiplier (premium for proven quality)
- **4.8★ workflow**: 1.276x multiplier
- **3★ workflow**: 1.06x multiplier

### Constraints
- **Min/Max**: 50-2000 tokens
- **Market comparison**: ±30% of median for similar workflows
- **Transparent**: Full breakdown shown in UI

### ROI Display
Each workflow prominently displays ROI:
```
ROI = (tokens_saved / price) × 100
```

**Example**: Ohio taxes workflow
- Saves: 10,350 tokens
- Price: 1,981 tokens
- **ROI: 522%** 🎯

### Pricing Breakdown UI
```
Base: 1,552 (15% of 10,350 saved)
→ Quality adjusted (4.8★): ×1.28
→ Final: 1,981 tokens
```

**Backend Module**: `backend/pricing.py`
**Update Script**: `backend/update_pricing.py`
**API Endpoint**: `GET /api/pricing/<workflow_id>`

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python api.py
```

Backend will start on `http://localhost:5001`

### Frontend Setup

```bash
# Install dependencies (from project root)
npm install

# Run development server
npm run dev
```

Frontend will start on `http://localhost:3000`

### Access the App
- **Landing page**: http://localhost:3000
- **Marketplace**: http://localhost:3000/marketplace
- **Backend API**: http://localhost:5001

## 📦 What's Included

### 8 Hyper-Specific Workflows

1. **Ohio 2024 IT-1040** (W2, Itemized, Married)
   - 69% token savings | 4.8★ rating | 47 uses

2. **California 2024 Form 540** (W2, Standard Deduction)
   - 67% token savings | 4.9★ rating | 89 uses

3. **Tokyo 5-Day Family Trip** (Kids 3-8, Stroller Accessible)
   - 73% token savings | 4.7★ rating | 34 uses

4. **Stripe Invoice Parser** (Multi-Currency, Line Items)
   - 66% token savings | 4.9★ rating | 156 uses

5. **Zillow Columbus OH Search** (3bed+, <$400k, School >7)
   - 65% token savings | 4.6★ rating | 28 uses

6. **LinkedIn B2B Cold Outreach** (Polite, Relationship-Preserving)
   - 60% token savings | 4.8★ rating | 92 uses

7. **Nebraska Self-Employed Taxes** (Quarterly Estimates)
   - 70% token savings | 4.7★ rating | 19 uses

8. **PDF Medical Records Parser** (Vitals, Medications, Diagnoses)
   - 65% token savings | 4.6★ rating | 63 uses

## 🎬 Demo Flow

1. **Select Scenario** - Choose from 3 demo scenarios
2. **Search Marketplace** - Vector similarity search across workflows
3. **View Results** - Browse matching workflows with ratings
4. **Purchase Workflow** - Download workflow template (200 tokens)
5. **Execute** - Run locally with private data (800 tokens)
6. **Compare** - See 70%+ token savings vs. from scratch
7. **Rate** - Provide feedback to improve quality

## 🔒 Privacy-First Design

**Two-layer architecture:**

**Public (sent to marketplace):**
```json
{
  "task_type": "tax_filing",
  "state": "ohio",
  "income_bracket": "80k-100k"  // Bucketed, not exact
}
```

**Private (stays local):**
```json
{
  "name": "John Smith",
  "ssn": "123-45-6789",
  "exact_income": 87432.18
  // Never sent to marketplace
}
```

## 🧪 Testing the API

### Search for workflows
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "tax_filing",
    "state": "ohio",
    "year": 2024
  }'
```

### Purchase a workflow
```bash
curl -X POST http://localhost:5000/api/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "ohio_w2_itemized_2024"
  }'
```

### Rate a workflow
```bash
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "ohio_w2_itemized_2024",
    "vote": "up"
  }'
```

## 📊 Key Metrics (Mock for Demo)

- **2,400 workflows** traded
- **$12k** in token costs saved
- **70%+ average** token savings
- **4.8★ average** workflow rating

## 🛠️ Tech Stack

**Backend:**
- Flask 3.0 - Web framework
- sentence-transformers - Embedding search
- scikit-learn - Cosine similarity
- CORS enabled for frontend

**Frontend:**
- React 18 - UI framework
- Tailwind CSS - Styling
- Recharts - Token comparison charts
- Lucide React - Icons
- Vite - Build tool

## 📝 Project Structure

```
treehacks-2026/
├── backend/
│   ├── api.py              # Main Flask app with endpoints
│   ├── matcher.py          # Embedding-based search
│   ├── sanitizer.py        # Privacy filter
│   ├── workflows.json      # 8 workflow examples
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Demo.jsx            # Main demo orchestrator
│   │   │   ├── WorkflowCard.jsx    # Workflow display card
│   │   │   └── TokenComparison.jsx # Savings visualization
│   │   ├── App.jsx         # Root component
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── vite.config.js
├── idea.md                 # Original concept document
└── README.md              # This file
```

## 🎯 Success Criteria

✅ Show 70%+ token savings on multiple tasks
✅ Workflows have realistic ratings/usage stats
✅ Privacy sanitization visible (before/after)
✅ Demo runs smoothly in <3 min

## 🚢 Deployment

### Backend (Railway/Render)
```bash
cd backend
# Follow platform-specific deploy instructions
```

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel
```

## 💡 Key Insights

1. **Specificity is critical** - "Ohio 2024 IT-1040, W2, itemized, married" not just "tax filing"
2. **Network effects** - More usage → better workflows → more users
3. **Privacy-first** - Workflows are templates, not data
4. **Domain knowledge** - Captures nuances agents miss ("Ohio has NO SALT cap")

## 🎤 Pitch One-Liner

"StackOverflow for AI agents. Reuse proven reasoning workflows for specific tasks. Save 70% tokens. Privacy-preserving. Infrastructure for the agent economy."

---

Built for TreeHacks 2026 🌲