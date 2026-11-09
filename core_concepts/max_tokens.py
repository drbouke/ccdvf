"""Acme support assistant: write the weekly support report."""
import anthropic
from store_tools import DATA

tickets = (DATA / "tickets.jsonl").read_text(encoding="utf-8")
prompt = ("Write this week's support report from these tickets: count per "
          "category, the three main problems, one action each.\n\n"
          + tickets)
client = anthropic.Anthropic()

# 300 tokens is too small for a report; 4,000 leaves room to finish
for limit in (300, 4000):
    response = client.messages.create(
        model="claude-haiku-5-5", max_tokens=limit,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in response.content if b.type == "text")
    print(f"max_tokens={limit}: {response.stop_reason}, "
          f"{response.usage.output_tokens} output tokens")
    print("  ends with:", repr(text[-50:]))  # where the text stopped
    if response.stop_reason != "max_tokens":
        break  # finished within the limit
