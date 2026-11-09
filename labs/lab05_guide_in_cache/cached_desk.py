"""Lab 5. Grant Desk reads the whole grant guide on every turn, from the cache.

Complete the four TODO steps, then run from the ccdvf folder:
    python run.py labs/lab05_guide_in_cache/cached_desk.py
"""
import json
import sys

import anthropic
from grants import GUIDE, TOOLS, run_tool
from meter import PRICES, text

MODEL = "claude-haiku-5-5"
WRITE, READ = 1.25, 0.10   # a cache write and a cache read, times the input price
RULES = (
    "You are Grant Desk, the claims assistant of the Acme Skills Fund. Assess the claim the officer names "
    "against the grant guide below, and cite its sections. Check every fact with the tools: the claim, the "
    "employer, the provider and the trainer on every training day, the deadline, and earlier claims for the "
    "same course run. Then call calculate_grant, decide the outcome as Section 9 says, call record_decision "
    "once, and summarize the decision in two sentences.\n\n")

# TODO 1: build SYSTEM as a list with one text block holding RULES followed by GUIDE, and mark it
# for caching with "cache_control": {"type": "ephemeral"}. Everything up to that mark (the tools, then
# this block) is cached for five minutes and read back on every later call.
SYSTEM = RULES + GUIDE


class CacheMeter:
    """Counts uncached, cache-written, and cache-read input tokens, and prices them."""

    def __init__(self):
        self.calls = self.uncached = self.written = self.read = self.output = 0

    def add(self, response):
        u = response.usage
        self.calls += 1
        # TODO 2: add this response's usage to the counters: input_tokens to uncached,
        # cache_creation_input_tokens to written, cache_read_input_tokens to read (each may be None,
        # so use "or 0"), and output_tokens to output.
        return response

    def cost(self, cached=True) -> float:
        price_in, price_out = (p / 1_000_000 for p in PRICES[MODEL])
        if not cached:   # what the same tokens cost with no cache: every input token at the full price
            return (self.uncached + self.written + self.read) * price_in + self.output * price_out
        # TODO 3: price the cached run: uncached tokens at price_in, written tokens at
        # price_in * WRITE, read tokens at price_in * READ, and output tokens at price_out.
        return 0.0

    def report(self) -> str:
        full = self.cost(cached=False)
        saved = 1 - self.cost() / full if full else 0.0
        return (f"{self.calls} call(s): {self.uncached:,} uncached, {self.written:,} written to the cache, "
                f"{self.read:,} read from it, {self.output:,} output\n"
                f"USD {self.cost():.5f} with the cache, USD {self.cost(cached=False):.5f} without it, "
                f"{saved:.0%} saved")


def assess(client, meter, claim_id: str) -> str:
    """The agent loop of Lab 4, with the cached system prompt."""
    messages = [{"role": "user", "content": f"Assess claim {claim_id}."}]
    for _ in range(20):
        response = meter.add(client.messages.create(
            model=MODEL, max_tokens=2000, system=SYSTEM, tools=TOOLS, messages=messages))
        u = response.usage
        # TODO 4: print one line per call with the tokens written to and read from the cache,
        # for example "  call: 0 written, 3,412 read, 220 uncached".
        if response.stop_reason != "tool_use":
            return text(response)
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                result, is_error = run_tool(block.name, block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": result, "is_error": is_error})
        messages.append({"role": "user", "content": results})
    return "Stopped after 20 turns without a decision."


def main():
    claims = sys.argv[1:] or ["CLM-24002", "CLM-24005"]
    client = anthropic.Anthropic()
    meter = CacheMeter()
    for claim_id in claims:
        print(claim_id)
        print(assess(client, meter, claim_id), "\n")
    print(meter.report())


if __name__ == "__main__":
    main()
