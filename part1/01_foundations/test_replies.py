"""Acme support assistant: test a reply feature whose wording varies."""
import json

import anthropic
from meter import text
from store_tools import DATA

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])  # T-1001: charged twice for order ord_20931
client = anthropic.Anthropic()


def reply() -> str:
    response = client.messages.create(
        model="claude-haiku-5-5", max_tokens=1500,  # thinking plus one sentence
        system=("Acknowledge the ticket in one sentence of at most 20 words "
                "and quote its order number."),
        messages=[{"role": "user", "content": ticket["text"]}])
    return text(response)


replies = [reply() for _ in range(3)]  # the same request, three times
for r in replies:  # word count and the end of each reply
    print(f"- {len(r.split())} words, ends: ...{r[-34:]}")
exact = all(r == replies[0] for r in replies)  # one fixed string
props = all("ord_20931" in r and len(r.split()) <= 20 for r in replies)
print("exact text test:", "pass" if exact else "FAIL")
print("property test:  ", "pass" if props else "FAIL")
