"""Acme support assistant: the same hard ticket at low and at high effort."""
import json

import anthropic
from store_tools import DATA, POLICY

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])  # T-1001: charged twice for one blender
client = anthropic.Anthropic()

for effort in ("low", "high"):
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=4000,  # room for thinking and the answer
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": effort},  # how deeply Claude reasons
        system="Decide what Acme owes the customer. Policy:\n" + POLICY,
        messages=[{"role": "user", "content": ticket["text"]}],
    )
    kinds = [block.type for block in response.content]
    print(f"effort={effort}: blocks {kinds}, "
          f"{response.usage.output_tokens} output tokens")
