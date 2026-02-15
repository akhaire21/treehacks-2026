"""
run_all.py — Run all agent demos with rich output.

Usage:
    python run_all.py              # Run all demos
    python run_all.py --tax        # Just tax agent
    python run_all.py --shop       # Just shopping agent
    python run_all.py --orchestrate # Just orchestrator

Exports traces as JSON for frontend replay.
"""

import sys
import json
import os

from agent_runner import AgentTrace


def save_trace(trace: AgentTrace, filename: str):
    """Save trace to JSON for frontend consumption."""
    os.makedirs("traces", exist_ok=True)
    path = f"traces/{filename}"
    with open(path, "w") as f:
        json.dump(trace.to_dict(), f, indent=2, default=str)
    print(f"  💾 Trace saved to {path}")


def main():
    args = set(sys.argv[1:])
    run_all = not args or "--all" in args

    if run_all or "--tax" in args:
        print("\n" + "🟣" * 30)
        print("  DEMO 1: Tax Filing Agent")
        print("🟣" * 30)
        from tax_agent import run_tax_agent
        trace = run_tax_agent()
        save_trace(trace, "tax_agent_trace.json")

    if run_all or "--shop" in args:
        print("\n" + "🟢" * 30)
        print("  DEMO 2: Shopping Agent")
        print("🟢" * 30)
        from shopping_agent import run_shopping_agent
        trace = run_shopping_agent()
        save_trace(trace, "shopping_agent_trace.json")

    if run_all or "--orchestrate" in args:
        print("\n" + "🔵" * 30)
        print("  DEMO 3: Orchestrator Agent")
        print("🔵" * 30)
        from orchestrator_agent import run_orchestrator_agent
        trace = run_orchestrator_agent()
        save_trace(trace, "orchestrator_agent_trace.json")

    print("\n✅ All demos complete!")


if __name__ == "__main__":
    main()
