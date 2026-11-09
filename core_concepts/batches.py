"""Acme support assistant: label last night's tickets in one batch."""
import json
import time

import anthropic
from store_tools import DATA

SYSTEM = ("Label the customer ticket with one word: billing, delivery, "
          "returns, product, or account. Reply with the label only.")
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
tickets = {t["ticket_id"]: t for t in map(json.loads, lines)}
client = anthropic.Anthropic()

batch = client.messages.batches.create(requests=[
    {"custom_id": tid,  # matches each result to its ticket
     "params": {"model": "claude-haiku-5-5", "max_tokens": 10,  # one word
                "system": SYSTEM, "thinking": {"type": "disabled"},
                "messages": [{"role": "user", "content": t["text"]}]}}
    for tid, t in tickets.items()])
print(f"{batch.id}: {len(tickets)} requests, {batch.processing_status}")
start = time.perf_counter()
while batch.processing_status != "ended":
    time.sleep(30)  # results come in minutes or hours, not seconds
    batch = client.messages.batches.retrieve(batch.id)
print(f"ended after {time.perf_counter() - start:.0f} s: "
      f"{batch.request_counts.succeeded} succeeded, "
      f"{batch.request_counts.errored} errored")
same = sum(r.result.message.content[0].text.strip().lower()
           == tickets[r.custom_id]["label"]  # the senior agent's label
           for r in client.messages.batches.results(batch.id)
           if r.result.type == "succeeded")
print(f"{same} of {len(tickets)} match the senior agent's label")
