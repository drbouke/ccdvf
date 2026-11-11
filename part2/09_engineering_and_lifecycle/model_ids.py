"""Acme support assistant: which snapshot does each model ID run?"""
import json

import anthropic
from meter import text
from store_tools import DATA

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])  # T-1001: charged twice for one blender
client = anthropic.Anthropic()

for model_id in ("claude-haiku-4-5",            # an older dateless name
                 "claude-haiku-4-5-20251001",   # a dated snapshot
                 "claude-haiku-5-5"):           # dateless, from 4.6 on
    resolved = client.models.retrieve(model_id).id  # what the ID names now
    response = client.messages.create(
        model=model_id, max_tokens=10,  # a one-word label
        system="Label the ticket: billing, delivery or returns. One word.",
        messages=[{"role": "user", "content": ticket["text"]}])
    label = text(response).strip("*").lower()  # **Billing** becomes billing
    print(f"{model_id:25} names {resolved}")
    print(f"{'':25} ran   {response.model}: {label}")
