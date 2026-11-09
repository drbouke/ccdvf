"""Acme support assistant: answer one customer ticket."""
import json

import anthropic
from store_tools import DATA, POLICY

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[1])  # T-1002: a parcel held at the north hub

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,  # room for thinking plus an 80-word reply
    system=("You are an Acme support agent. Reply to the customer in at "
            "most 80 words. Apply this policy:\n" + POLICY),
    messages=[{"role": "user", "content": ticket["text"]}],
)

for block in response.content:  # a thinking block, then the text
    print(block.type)
    if block.type == "text":
        print("  " + block.text)
print("stop_reason:", response.stop_reason)
print(f"usage: {response.usage.input_tokens} in, "
      f"{response.usage.output_tokens} out")
