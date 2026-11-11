"""Acme support assistant: an edited tool description empties the cache."""
import copy
import json

import anthropic
from store_tools import DATA, POLICY, TOOLS

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])  # T-1001: charged twice for one blender
client = anthropic.Anthropic()
SYSTEM = [{"type": "text", "text": "Acme support agent. Policy:\n" + POLICY,
           "cache_control": {"type": "ephemeral"}}]  # caches tools + system


def ask(tools: list, label: str) -> None:
    usage = client.messages.create(
        model="claude-haiku-5-5", tools=tools,
        max_tokens=500,  # a short reply; only the usage matters
        system=SYSTEM, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": ticket["text"]}]).usage
    print(f"{label:24} written {usage.cache_creation_input_tokens or 0:>5}"
          f"  read {usage.cache_read_input_tokens or 0:>5}")


ask(TOOLS, "first request")
ask(TOOLS, "same prefix again")
edited = copy.deepcopy(TOOLS)
tool = next(t for t in edited if t["name"] == "get_order")
tool["description"] += " Use it before any refund."  # one sentence
ask(edited, "tool description edited")
ask(edited, "edited prefix again")
