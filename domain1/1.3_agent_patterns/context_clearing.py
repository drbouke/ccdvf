"""Context editing in a long session: an agent reviews 30 delayed orders one by one. Each order the agent reads adds about
570 tokens, so the conversation grows fast. With clearing on, the API removes old tool results once the input passes the
trigger and keeps the newest 3; the table shows the input size of every call and when results were cleared.

    python run.py domain1/1.3_agent_patterns/context_clearing.py          clearing on
    python run.py domain1/1.3_agent_patterns/context_clearing.py --off    the same session without clearing, to compare
"""
import json
import sqlite3
import sys
import anthropic
from meter import Meter, text
from pintar_tools import DB, TOOLS, run_tool

MODEL = "claude-haiku-5-5"
with sqlite3.connect(DB) as con:
    delayed = [r[0] for r in con.execute(
        "SELECT order_id FROM orders WHERE status = 'delayed' "
        "ORDER BY order_id LIMIT 30")]
task = ("Review these delayed orders one at a time with get_order, one call "
        "per turn. Keep a running note of each order whose parcel is held "
        "because the address could not be verified. At the end, list those "
        "orders with the customer id and the hub. Orders: "
        + ", ".join(delayed))

client = anthropic.Anthropic()
meter = Meter(MODEL)
use_clearing = "--off" not in sys.argv
messages = [{"role": "user", "content": task}]
CLEARING = {"edits": [{"type": "clear_tool_uses_20250919",
                       "trigger": {"type": "input_tokens", "value": 8000},
                       "keep": {"type": "tool_uses", "value": 3}}]}
print(f"{'call':>4} {'input tokens':>12}  cleared")
while True:
    extra = {"context_management": CLEARING} if use_clearing else {}
    resp = meter.add(client.beta.messages.create(
        model=MODEL, max_tokens=2000,
        betas=["context-management-2025-06-27"],
        tools=[t for t in TOOLS if t["name"] == "get_order"],
        messages=messages, **extra))
    applied = getattr(resp, "context_management", None)
    edits = (applied.applied_edits if applied else None) or []
    cleared = ", ".join(f"{e.cleared_tool_uses} tool results "
                        f"({e.cleared_input_tokens:,} tokens)" for e in edits)
    print(f"{meter.calls:>4} {resp.usage.input_tokens:>12,}  {cleared}")
    calls = [b for b in resp.content if b.type == "tool_use"]
    if resp.stop_reason != "tool_use" or not calls:
        break
    messages.append({"role": "assistant", "content": resp.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": b.id,
         "content": run_tool(b.name, b.input)}
        for b in calls]})
print("\n" + text(resp))
print(f"\nClearing {'on' if use_clearing else 'off'}: " + meter.report())
