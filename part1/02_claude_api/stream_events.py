"""Acme support chat: the events of one streamed reply, in arrival order."""
import json

import anthropic
from store_tools import DATA

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[2])  # T-1003, a blender with a cracked jug
client = anthropic.Anthropic()
deltas = 0

with client.messages.stream(
        model="claude-haiku-5-5", max_tokens=300,
        thinking={"type": "disabled"},  # text blocks only, a short list
        system="Reply to the Acme customer in at most 40 words.",
        messages=[{"role": "user", "content": ticket["text"]}]) as stream:
    for event in stream:  # each server-sent event, as the SDK reads it
        if event.type == "content_block_delta":
            deltas += 1
            if deltas <= 2:  # the first two pieces of text are enough
                print(f"{event.type}  {event.delta.text!r}")
        elif event.type == "message_delta":
            print(f"{event.type}  stop_reason={event.delta.stop_reason}"
                  f"  output_tokens={event.usage.output_tokens}")
        elif not event.type.startswith(("text", "content_block_delta")):
            print(event.type)  # start and stop events
print(f"{deltas} text deltas in all")
