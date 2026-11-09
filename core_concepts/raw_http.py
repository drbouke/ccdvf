"""Acme support assistant: the ticket reply, sent with no SDK."""
import json
import os
from urllib.request import Request, urlopen

from store_tools import DATA, POLICY

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[1])  # T-1002, the same ticket
body = {
    "model": "claude-haiku-5-5",
    "max_tokens": 1000,  # the same limits as the SDK call
    "system": ("You are an Acme support agent. Reply to the customer in at "
               "most 80 words. Apply this policy:\n" + POLICY),
    "messages": [{"role": "user", "content": ticket["text"]}],
}
request = Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps(body).encode(),
    headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
             "anthropic-version": "2026-10-21",  # API version of this code
             "content-type": "application/json"})

with urlopen(request, timeout=60) as response:  # seconds to wait
    reply = json.load(response)
    print("HTTP status:", response.status, "| stop_reason:",
          reply["stop_reason"])
print(f"usage: {reply['usage']['input_tokens']} in, "
      f"{reply['usage']['output_tokens']} out")
