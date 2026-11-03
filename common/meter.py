"""Measures what each example costs: tokens, US dollars and seconds.

Prices per million tokens from the Anthropic pricing page (November 2026). Haiku 5.5 is priced at the rate for prompts
up to 100,000 tokens, which covers every example here.
"""
import threading
import time

PRICES = {  # model: (input, output) in USD per million tokens
    'claude-haiku-5-5': (0.10, 0.50),
    'claude-sonnet-5-5': (2.00, 10.00),
    'claude-opus-5-5': (4.00, 20.00),
}


class Meter:
    def __init__(self, model):
        self.model = model
        self.calls = self.input_tokens = self.output_tokens = 0
        self.started = time.perf_counter()
        self._lock = threading.Lock()   # examples call Claude from several threads

    def add(self, resp):
        """Count one Messages API response."""
        with self._lock:
            self.calls += 1
            self.input_tokens += resp.usage.input_tokens
            self.output_tokens += resp.usage.output_tokens
        return resp

    @property
    def cost(self):
        pin, pout = PRICES.get(self.model, (0.0, 0.0))
        return (self.input_tokens * pin + self.output_tokens * pout) / 1_000_000

    def report(self):
        secs = time.perf_counter() - self.started
        return (f'{self.calls} call(s), {self.input_tokens:,} input + {self.output_tokens:,} output tokens, '
                f'USD {self.cost:.5f}, {secs:.1f} s, model {self.model}')


def text(resp):
    """The text of a reply. Claude may return thinking and tool blocks too, and the last block is not always text."""
    return "".join(b.text for b in resp.content if b.type == "text").strip()
