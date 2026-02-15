# Mark AI — Pitch Demo

**Side-by-side comparison: AI agent WITH vs WITHOUT `marktools`**

Same task. Same model. Dramatically different results.

## Quick Start

```bash
# From the project root
python demo/run_demo.py
```

That's it. No API keys needed. No backend required. Fully self-contained.

## Options

| Flag | Description |
|------|-------------|
| `--fast` | Skip typing animations (for testing) |
| `--json` | Export results to `demo/demo_results.json` |

```bash
# Fast mode (good for rehearsal)
python demo/run_demo.py --fast

# Export comparison data
python demo/run_demo.py --json
```

## What It Shows

### ❌ Without marktools (baseline)
A raw Claude agent tries to file Ohio 2024 taxes from scratch:
- **8 reasoning steps**, burning **4,390 tokens**
- **4 errors**: wrong SALT cap, outdated brackets, missed credits, dismissed local taxes
- **37.5% accuracy** — only 3/8 steps correct
- Taxpayer would **overpay ~$2,650** following this advice

### ✅ With marktools (enhanced)
The same Claude agent, but with `pip install marktools`:
- **4 steps**: estimate → buy → present → rate
- **3 tool calls** to the Mark AI marketplace
- **100% accuracy** — every edge case caught by expert-verified workflow
- **6 critical edge cases** surfaced automatically
- Correct tax estimate with all required forms

### 📊 Scorecard
| Metric | Without | With | Δ |
|--------|---------|------|---|
| Accuracy | 37.5% | 100% | **+62.5pp** |
| Tokens | 4,390 | 1,330 | **−70%** |
| Latency | 8.5s | 3.8s | **−55%** |
| Errors | 4 | 0 | **−100%** |
| Edge Cases | 0 caught | 6 caught | **∞** |

## For the Pitch

1. Open a terminal with large font (⌘+)
2. Run `python demo/run_demo.py`
3. Let the animation play — it takes ~45 seconds
4. The scorecard at the end is the money slide
5. Point out the **real-world dollar impact**: the baseline would cost a taxpayer $2,650+

## File Structure

```
demo/
├── run_demo.py           # Main entry point — run this
├── without_marktools.py  # Baseline agent simulation
├── with_marktools.py     # Enhanced agent simulation
├── demo_results.json     # Generated when using --json
└── README.md             # This file
```
