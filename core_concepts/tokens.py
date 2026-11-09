"""Acme support assistant: budget the nightly ticket triage."""
import json

import anthropic
from meter import PRICES
from store_tools import DATA, POLICY

MODEL = "claude-haiku-5-5"  # the triage model: fast and low cost
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY


def input_tokens(text: str, system: str | None = None) -> int:
    """Input tokens of one request, counted without generating a reply."""
    request = {"model": MODEL,
               "messages": [{"role": "user", "content": text}]}
    if system:
        request["system"] = system
    return client.messages.count_tokens(**request).input_tokens


lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
tickets = [json.loads(line)["text"] for line in lines]  # tonight's 60
alone = [input_tokens(t) for t in tickets]
with_policy = [input_tokens(t, system=POLICY) for t in tickets]
total = sum(with_policy)
cost = total * PRICES[MODEL][0] / 1_000_000  # USD per million input

print(f"{len(tickets)} tickets: {min(alone)} to {max(alone)} tokens")
print(f"Request with the policy: {min(with_policy):,} to "
      f"{max(with_policy):,}")
print(f"Whole run: {total:,} input tokens, USD {cost:.4f}")
print(f"The policy is {1 - sum(alone) / total:.0%} of them")
