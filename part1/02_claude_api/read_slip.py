"""Acme support assistant: read the courier's exception slip, an image."""
import base64
import json

import anthropic
from meter import text
from store_tools import DATA, get_order

slip = base64.b64encode((DATA / "slip_ord_21044.png").read_bytes()).decode()
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1500,  # room for thinking and a short JSON object
    messages=[{"role": "user", "content": [
        {"type": "image",  # the picture goes in as an image block
         "source": {"type": "base64", "media_type": "image/png",
                    "data": slip}},
        {"type": "text", "text": "Return only JSON with tracking_number, "
                                 "status, reason and held_at from this slip."},
    ]}],
)
raw = text(response).strip().removeprefix("```json").removesuffix("```")
# Claude may wrap the JSON in a code fence; the line above removes it
found = json.loads(raw)
print(json.dumps(found, indent=2))

record = json.loads(get_order("ord_21044"))  # what the store database holds
print("tracking number matches:",
      found["tracking_number"] == record["shipment"]["tracking_no"])
print(f"usage: {response.usage.input_tokens} in, "
      f"{response.usage.output_tokens} out")
