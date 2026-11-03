"""The tool-use loop on a support case: Claude looks up the customer and the order, reads the policy, and answers."""
import json
import anthropic
from meter import Meter, text
from pintar_tools import TOOLS, run_tool

MODEL = "claude-haiku-5-5"
SYSTEM = ("You are a Pintar customer service agent. Check every fact with the tools before you answer, "
          "cite the policy section behind each promise, and end with the next step and its time frame.")
TICKET = ("From aisyah.rahman@gmail.com: The blender arrived with a cracked jug, and I think I was "
          "charged twice for it. Please sort out both.")

client = anthropic.Anthropic()
meter = Meter(MODEL)
messages = [{"role": "user", "content": TICKET}]
while True:
    resp = meter.add(client.messages.create(
        model=MODEL, max_tokens=3000, system=SYSTEM,
        tools=TOOLS, messages=messages))
    if resp.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": resp.content})
    results = []
    for b in resp.content:
        if b.type == "tool_use":
            print(f"-> {b.name}({json.dumps(b.input)})")
            results.append({"type": "tool_result", "tool_use_id": b.id,
                            "content": run_tool(b.name, b.input)})
    messages.append({"role": "user", "content": results})
print("\n" + text(resp))
print("\n" + meter.report())
