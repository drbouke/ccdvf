"""Acme support assistant: watch a tool call arrive in a stream."""
import json

import anthropic
from store_tools import DATA, TOOLS


def parses(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[1])  # T-1002: a parcel held at the north hub
client = anthropic.Anthropic()
with client.messages.stream(
    model="claude-haiku-5-5", max_tokens=1000, tools=TOOLS,
    thinking={"type": "disabled"},  # keeps the event list short
    messages=[{"role": "user", "content": ticket["text"]}],
) as stream:
    so_far = ""
    for event in stream:
        if (event.type == "content_block_delta"
                and event.delta.type == "input_json_delta"):
            so_far += event.delta.partial_json
            print(f"{so_far!r:28} valid JSON: {parses(so_far)}")
        elif event.type == "content_block_stop" and so_far:
            print("block closed, input:", json.loads(so_far))
            so_far = ""  # the next tool call starts empty
