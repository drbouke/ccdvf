"""Routing, measured: Claude sorts 60 tickets into five queues, and the script compares its choices with the
labels a senior agent gave.

    python run.py domain1/1.1_agent_architecture/route_tickets.py             one call per ticket
    python run.py domain1/1.1_agent_architecture/route_tickets.py --votes 3   three calls per ticket, the majority wins (parallelization by voting)
"""
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import anthropic
from meter import Meter
from store_tools import DATA

MODEL = "claude-haiku-5-5"
QUEUES = ["billing", "delivery", "returns", "product", "account"]
ROUTE = {"name": "route", "description": "Send the ticket to exactly one queue.",
         "input_schema": {"type": "object",
                          "properties": {"queue": {"type": "string", "enum": QUEUES},
                                         "reason": {"type": "string", "description": "One short sentence"}},
                          "required": ["queue", "reason"]}}
SYSTEM = """You route Acme customer tickets to one queue.
billing: charges, duplicate or wrong amounts, refunds already approved but not received, invoices, promo codes, failed payments
delivery: where is my order, delays, failed or wrong deliveries, address or order changes before dispatch, shipping options
returns: damaged, defective, wrong, used or unwanted items the customer wants to return, replace or get money back for
product: questions before buying or about using a product: compatibility, specifications, warranty terms
account: login, password, OTP, two-factor, profile details, data deletion, app or website errors
When a ticket mixes issues, choose the issue the customer asks to fix first."""

client = anthropic.Anthropic()
meter = Meter(MODEL)


def classify(text):
    resp = meter.add(client.messages.create(
        model=MODEL, max_tokens=300, system=SYSTEM, tools=[ROUTE],
        tool_choice={"type": "tool", "name": "route"},
        messages=[{"role": "user", "content": text}]))
    return next(b.input["queue"] for b in resp.content if b.type == "tool_use")


def decide(ticket, votes):
    counts = Counter(classify(ticket["text"]) for _ in range(votes))
    return counts.most_common(1)[0][0], dict(counts)


votes = 1
if "--votes" in sys.argv:
    votes = int(sys.argv[sys.argv.index("--votes") + 1])
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
tickets = [json.loads(line) for line in lines]
with ThreadPoolExecutor(max_workers=8) as pool:  # calls run at the same time
    answers = list(pool.map(lambda t: decide(t, votes), tickets))

right = [a == t["label"] for (a, _), t in zip(answers, tickets)]
print(f"Accuracy with {votes} vote(s) per ticket: {sum(right)}/{len(tickets)} = {sum(right) / len(tickets):.0%}\n")
for q in QUEUES:
    idx = [i for i, t in enumerate(tickets) if t["label"] == q]
    print(f"  {q:9} {sum(right[i] for i in idx)}/{len(idx)}")
print("\nMisrouted:")
for (a, counts), t, ok in zip(answers, tickets, right):
    if not ok:
        split = f" votes {counts}" if votes > 1 else ""
        print(f"  {t['ticket_id']} expected {t['label']}, got {a}{split}: {t['text'][:70]}")
print("\n" + meter.report())
