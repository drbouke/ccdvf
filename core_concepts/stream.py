"""Acme support assistant: stream a reply into the support chat."""
import json
import time

import anthropic
from store_tools import DATA, POLICY

lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[2])  # T-1003: a blender with a cracked jug
client = anthropic.Anthropic()
start = time.perf_counter()

with client.messages.stream(
    model="claude-haiku-5-5",
    max_tokens=1500,  # a full chat reply, with no word limit
    system="You are an Acme support agent. Apply this policy:\n" + POLICY,
    messages=[{"role": "user", "content": ticket["text"]}],
) as stream:
    for count, piece in enumerate(stream.text_stream, start=1):
        if count <= 3:  # the first pieces show when the reply starts
            print(f"{time.perf_counter() - start:5.2f} s  {piece!r}")
    final = stream.get_final_message()

print(f"{time.perf_counter() - start:5.2f} s  done, {count} pieces, "
      f"{final.usage.output_tokens} output tokens")
