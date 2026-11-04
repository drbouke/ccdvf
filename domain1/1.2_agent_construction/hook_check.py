"""The refund hook on store orders, without an agent. A hook is plain code, so the same order always receives the same
decision, regardless of what the model is told."""
import asyncio
import sqlite3
from store_tools import DB
from refund_hook import cap_refunds

with sqlite3.connect(DB) as con:
    earlier = con.execute("SELECT order_id FROM refunds LIMIT 1").fetchone()[0]
REQUESTS = [
    ("ord_20931", 289.00, "duplicate charge"),
    ("ord_21500", 899.00, "damaged on arrival"),
    (earlier, 50.00, "goodwill credit"),
]
for order_id, amount, reason in REQUESTS:
    event = {"hook_event_name": "PreToolUse", "tool_name": "mcp__orders__issue_refund",
             "tool_input": {"order_id": order_id, "amount": amount, "reason": reason}}
    out = asyncio.run(cap_refunds(event, "toolu_check", None))
    verdict = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "allowed")
    print(f"{order_id}  ${amount:>7.2f}  {reason:20}  -> {verdict}")
