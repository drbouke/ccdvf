"""Acme support assistant: a routing workflow. One call labels the ticket;
the code sends it to the prompt written for that kind of ticket."""
import json

import anthropic
from meter import Meter, text
from store_tools import DATA

MODEL = "claude-haiku-5-5"
ROUTES = {  # label: the specialized system prompt
    "billing": "You handle payments. Name the charge and the refund time.",
    "delivery": "You handle parcels. Name the next courier step and date.",
    "returns": "You handle returns. Name the return option that applies.",
}
client = anthropic.Anthropic()
meter = Meter(MODEL)
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()

for ticket in map(json.loads, lines[:3]):
    label = text(meter.add(client.messages.create(  # step 1: classify
        model=MODEL, max_tokens=10, thinking={"type": "disabled"},
        system=("Label the ticket with one word: billing (payments), "
                "delivery (parcels on the way) or returns (items received)."),
        messages=[{"role": "user", "content": ticket["text"]}])))
    label = label.lower().strip(" .")  # "Billing." becomes "billing"
    reply = text(meter.add(client.messages.create(  # step 2: specialist
        model=MODEL, max_tokens=1500,  # room for thinking and one sentence
        system=ROUTES.get(label, ROUTES["returns"]) +
        " Answer in one sentence of at most 15 words.",
        messages=[{"role": "user", "content": ticket["text"]}])))
    print(f"{ticket['ticket_id']} -> {label}: {reply}")
print(meter.report())
