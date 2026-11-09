"""Usage meter of the Acme support assistant: tokens, cost and time.

Prices are USD per million tokens, from the Anthropic pricing page
(November 2026). Claude Haiku 5.5 is priced at its rate for prompts of up
to 100,000 tokens, which covers every request in this project.
"""
import threading
import time

PRICES = {  # model: (input, output)
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}


class Meter:
    """Adds up the usage of every response passed to add()."""

    def __init__(self, model: str):
        self.model = model
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.started = time.perf_counter()
        self._lock = threading.Lock()  # routing calls Claude from threads

    def add(self, resp):
        """Count one Messages API response and return it unchanged."""
        with self._lock:
            self.calls += 1
            self.input_tokens += resp.usage.input_tokens
            self.output_tokens += resp.usage.output_tokens
        return resp

    @property
    def cost(self) -> float:
        price_in, price_out = PRICES.get(self.model, (0.0, 0.0))
        return (self.input_tokens * price_in
                + self.output_tokens * price_out) / 1_000_000

    def report(self) -> str:
        seconds = time.perf_counter() - self.started
        return (f"{self.calls} call(s), {self.input_tokens:,} input + "
                f"{self.output_tokens:,} output tokens, "
                f"USD {self.cost:.5f}, {seconds:.1f} s, model {self.model}")


def text(resp) -> str:
    """The text of a reply, without thinking or tool blocks."""
    return "".join(b.text for b in resp.content if b.type == "text").strip()
