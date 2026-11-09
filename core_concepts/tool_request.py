"""Acme support assistant: let Claude look up the facts of a ticket."""
import json

import anthropic
from store_tools import DATA, TOOLS

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[1])  # T-1002: a parcel held at the north hub
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=800,  # a tool request is short
    tools=TOOLS,  # names, descriptions and input schemas
    system="You are an Acme support agent. Check the facts.",
    messages=[{"role": "user", "content": ticket["text"]}],
)

print("stop_reason:", response.stop_reason)  # tool_use: Claude is asking
for block in response.content:
    if block.type == "tool_use":
        print(json.dumps(block.to_dict(), indent=2))
