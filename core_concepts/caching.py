"""Acme support assistant: answer the morning queue with the policy cached."""
import json

import anthropic
from meter import PRICES
from store_tools import DATA, POLICY

MODEL = "claude-haiku-5-5"
WRITE, READ = 1.25, 0.10  # cache write and cache read, times the input price
SYSTEM = [{
    "type": "text",
    "text": ("You are an Acme support agent. Reply to the customer in at "
             "most 80 words. Apply this policy:\n" + POLICY),
    "cache_control": {"type": "ephemeral"},  # cache up to here, 5 minutes
}]

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
client = anthropic.Anthropic()
price = PRICES[MODEL][0] / 1_000_000  # USD per input token

for line in lines[:3]:  # the first three tickets of the morning queue
    ticket = json.loads(line)
    usage = client.messages.create(
        model=MODEL, max_tokens=1000, system=SYSTEM,  # thinking + 80 words
        messages=[{"role": "user", "content": ticket["text"]}]).usage
    written = usage.cache_creation_input_tokens or 0
    read = usage.cache_read_input_tokens or 0
    cost = (usage.input_tokens + written * WRITE + read * READ) * price
    full = (usage.input_tokens + written + read) * price
    print(f"{ticket['ticket_id']}: {written:,} written, {read:,} read, "
          f"{usage.input_tokens} not cached")
    print(f"  input USD {cost:.7f}, without the cache {full:.7f}")
