"""Acme support: a tool error Claude can act on, shown as a trace."""
import json
import sys

import anthropic
from store_tools import TOOLS, run_tool

GENERIC = "--generic" in sys.argv  # send "failed" instead of a useful error
HINT = ("Unknown order id. find_customer with the customer's email lists "
        "their orders with the correct ids.")
messages = [{"role": "user", "content": "This is ryan.clark7@example.com. "
             "Where is my order ord_2104? It should have arrived by now."}]
client = anthropic.Anthropic()
for _ in range(4):  # at most four rounds
    resp = client.messages.create(model="claude-haiku-5-5", max_tokens=1500,
                                  tools=TOOLS, messages=messages)
    if resp.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": resp.content})
    results = []
    for b in [b for b in resp.content if b.type == "tool_use"]:
        out = run_tool(b.name, b.input)
        failed = "not found" in out or "No customer" in out
        if failed:
            out = "failed" if GENERIC else HINT
        print(f"tool_use {b.name} {json.dumps(b.input)}")
        print(f"  tool_result is_error={failed}: {out[:52]}")
        results.append({"type": "tool_result", "tool_use_id": b.id,
                        "content": out, "is_error": failed})
    messages.append({"role": "user", "content": results})
answer = next(b.text for b in resp.content if b.type == "text")
print("answer: " + answer.split("\n")[0][:150])  # its first line
