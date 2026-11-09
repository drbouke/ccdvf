"""Acme ticket labels: a bare prompt and a constrained prompt, compared."""
import json
from collections import Counter

import anthropic
from store_tools import DATA

BARE = "You are a support classifier. Classify the ticket."
CONSTRAINED = """Classify the Acme customer ticket into exactly one of:
billing, delivery, returns, product, account. Reply with the label only.
<example><ticket>Two charges for one order.</ticket>
<label>billing</label></example>
<example><ticket>The OTP never arrives.</ticket>
<label>account</label></example>"""
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
client = anthropic.Anthropic()

for name, system in [("bare", BARE), ("constrained", CONSTRAINED)]:
    replies, right = Counter(), 0
    for line in lines[:10]:  # the first ten tickets
        ticket = json.loads(line)
        msg = client.messages.create(
            model="claude-haiku-5-5", max_tokens=200, system=system,
            thinking={"type": "disabled"},
            messages=[{"role": "user", "content": ticket["text"]}])
        reply = msg.content[0].text.strip()
        replies[reply[:40]] += 1
        right += reply == ticket["label"]  # exactly the label, as code needs
    print(f"{name}: {len(replies)} different replies, {right} of 10 labels")
    for reply, n in replies.most_common(2):
        print(f"  {n} x {reply!r}")
