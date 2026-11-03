"""The tool-use round trip, request by request: what each request sends, why each response stopped, and how every
tool_result answers a tool_use by its id. The question is about Ravi's monitor, held at a courier hub."""
import json
import anthropic
from meter import Meter, text
from pintar_tools import TOOLS, run_tool

MODEL = "claude-haiku-5-5"
client = anthropic.Anthropic()
meter = Meter(MODEL)
messages = [{"role": "user", "content": "Where is order ord_21044 now, and why has it not arrived?"}]
n = 0
while True:
    n += 1
    print(f"request {n}: {len(messages)} message(s), last role {messages[-1]['role']}, {len(TOOLS)} tools")
    resp = meter.add(client.messages.create(model=MODEL, max_tokens=3000, tools=TOOLS, messages=messages))
    print(f"response {n}: stop_reason={resp.stop_reason}, blocks: " + ", ".join(b.type for b in resp.content))
    calls = [b for b in resp.content if b.type == "tool_use"]
    if resp.stop_reason != "tool_use" or not calls:
        break
    results = []
    for b in calls:
        out = run_tool(b.name, b.input)
        print(f"  tool_use {b.id} {b.name} {json.dumps(b.input)}")
        print(f"  tool_result for {b.id}: {len(out):,} characters of JSON")
        results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
    messages.append({"role": "assistant", "content": resp.content})
    messages.append({"role": "user", "content": results})
print("\n" + text(resp))
print("\n" + meter.report())
