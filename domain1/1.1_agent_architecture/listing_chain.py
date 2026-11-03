"""Prompt chaining with a gate: Claude drafts an English product listing from the specs, your code checks it, and only
a listing that passes goes on to the Malay translation."""
import json
import re
import anthropic
from meter import Meter, text
from pintar_tools import DATA

MODEL = "claude-haiku-5-5"
BANNED = ["best", "guaranteed", "100%", "perfect", "number one"]   # claims Pintar may not make
client = anthropic.Anthropic()
meter = Meter(MODEL)


def ask(prompt, max_tokens=2500):
    resp = meter.add(client.messages.create(model=MODEL, max_tokens=max_tokens,
                                            messages=[{"role": "user", "content": prompt}]))
    return text(resp)


def gate(text, product):
    """Checks between the two calls; an empty list means the draft passes."""
    problems = []
    if len(text.split()) > 120:
        problems.append(f"{len(text.split())} words, limit 120")
    if product["specs"]["warranty"].split()[0] not in text:
        problems.append("warranty period missing")
    for w in BANNED:
        if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text, re.I):
            problems.append(f'banned claim "{w}"')
    return problems


specs = (DATA / "product_specs.json").read_text(encoding="utf-8")
for product in json.loads(specs):
    draft = ask("Write a product listing for an online store in Malaysia, "
                "at most 110 words: one line on who it is for, three "
                "benefits as bullets, and a specs line that includes the "
                f"warranty. Use only these facts:\n{json.dumps(product)}")
    problems = gate(draft, product)
    result = "FAILED: " + "; ".join(problems) if problems else "passed"
    print(f"=== {product['name']}: gate {result}")
    if problems:
        print(draft + "\n")
        continue
    malay = ask("Translate this product listing into Bahasa Malaysia for "
                "Malaysian shoppers. Keep the bullets, numbers and units "
                "exactly.\n\n" + draft)
    print(malay + "\n")
print(meter.report())
