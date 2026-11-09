"""Acme triage: label all 60 tickets at once, at most 10 in flight."""
import asyncio
import json
import time

from anthropic import AsyncAnthropic
from store_tools import DATA

SYSTEM = ("Label the customer ticket with one word: billing, delivery, "
          "returns, product, or account. Reply with the label only.")
tickets = [json.loads(line) for line in (DATA / "tickets.jsonl").read_text(
    encoding="utf-8").splitlines()]
client = AsyncAnthropic()
limit = asyncio.Semaphore(10)  # at most 10 requests in flight

async def label(ticket):
    async with limit:  # waits here while 10 requests are running
        msg = await client.messages.create(
            model="claude-haiku-5-5", max_tokens=10, system=SYSTEM,
            thinking={"type": "disabled"},  # one word, no thinking
            messages=[{"role": "user", "content": ticket["text"]}])
        return msg.content[0].text.strip().lower()


async def main():
    start = time.perf_counter()
    labels = await asyncio.gather(*(label(t) for t in tickets))
    same = sum(lab == t["label"] for lab, t in zip(labels, tickets))
    print(f"{len(labels)} tickets in {time.perf_counter() - start:.1f} s")
    print(f"{same} of {len(tickets)} match the senior agent's label")

asyncio.run(main())
