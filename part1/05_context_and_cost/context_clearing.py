"""Context editing: an agent reviews 30 delayed orders, one per turn."""
import sqlite3, sys, anthropic
from meter import Meter, text
from store_tools import DB, TOOLS, run_tool
MODEL = "claude-haiku-5-5"
ids = [r[0] for r in sqlite3.connect(DB).execute("SELECT order_id FROM "
       "orders WHERE status = 'delayed' ORDER BY order_id LIMIT 30")]
task = ("Review these orders one at a time with get_order, one call per "
        "turn. At the end, list each order held because the address could "
        "not be verified, with its customer id and hub. " + ", ".join(ids))
CLEARING = {"edits": [{"type": "clear_tool_uses_20250919",
    "trigger": {"type": "input_tokens", "value": 8000},
    "keep": {"type": "tool_uses", "value": 3}}]}
extra = {} if "--off" in sys.argv else {"context_management": CLEARING}
client, meter = anthropic.Anthropic(), Meter(MODEL)
messages = [{"role": "user", "content": task}]
while True:
    resp = meter.add(client.beta.messages.create(
        model=MODEL, max_tokens=2000, betas=["context-management-2025-06-27"],
        tools=[t for t in TOOLS if t["name"] == "get_order"],
        messages=messages, **extra))
    cm = getattr(resp, "context_management", None)
    for e in (cm.applied_edits if cm else None) or []:
        print(f"call {meter.calls}: {resp.usage.input_tokens:,} input tokens"
              f" after clearing {e.cleared_tool_uses} results")
    calls = [b for b in resp.content if b.type == "tool_use"]
    if resp.stop_reason != "tool_use" or not calls:
        break
    messages.append({"role": "assistant", "content": resp.content})
    messages.append({"role": "user", "content": [{"type": "tool_result",
    "tool_use_id": b.id, "content": run_tool(b.name, b.input)} for b in calls]})
print(text(resp) + "\n\n" + meter.report())
