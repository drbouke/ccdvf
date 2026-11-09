"""Acme triage: every reply follows one JSON Schema."""
import json

import anthropic
from store_tools import DATA

SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": [
            "billing", "delivery", "returns", "product", "account"]},
        "needs_human": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["category", "needs_human", "summary"],
    "additionalProperties": False,
}
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
client = anthropic.Anthropic()
for line in lines[:3]:
    ticket = json.loads(line)
    msg = client.messages.create(
        model="claude-haiku-5-5", max_tokens=1000,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user",
                   "content": "Triage this Acme ticket. Keep the summary "
                   "under 12 words.\n" + ticket["text"]}])
    text = next(b.text for b in msg.content if b.type == "text")
    triage = json.loads(text)  # parses: the reply follows the schema
    print(f"{ticket['ticket_id']}: {triage['category']}, "
          f"needs_human={triage['needs_human']}")
    print(f"  {triage['summary']}")
