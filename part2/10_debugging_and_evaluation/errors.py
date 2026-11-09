"""Acme support: which API errors the SDK retries, and which need a fix."""
import json

import anthropic
from store_tools import DATA

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])  # T-1001, a duplicate charge
client = anthropic.Anthropic(max_retries=4)  # retries 408, 409, 429, 5xx
cases = {"no messages": [],
         "ticket T-1001": [{"role": "user", "content": ticket["text"]}]}

for name, messages in cases.items():
    try:
        msg = client.messages.create(model="claude-haiku-5-5",
                                     max_tokens=1000, messages=messages)
        print(f"{name}: {msg.stop_reason}, "
              f"{msg.usage.output_tokens} output tokens")
    except anthropic.RateLimitError:  # 429 after the retries ran out
        print(f"{name}: rate limited, queued for later")
    except anthropic.BadRequestError as e:  # 400: retrying cannot help
        print(f"{name}: {type(e).__name__}, status {e.status_code}")
        print(f"  {e.body['error']['message']}")
    except anthropic.APIStatusError as e:  # any other error status
        print(f"{name}: status {e.status_code}")
